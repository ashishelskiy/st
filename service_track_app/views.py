from django.shortcuts import render, redirect, get_object_or_404
from .forms import RepairRequestForm, RepairRequestEditForm
from .models import RepairRequest, Package, RequestHistory, RepairRequestPhoto, RepairRequestVideo

from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .decorators import role_required

from django.utils import timezone
from django.contrib import messages
from django.urls import reverse
from django.db.models import F, Count
from collections import defaultdict


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # перенаправляем в home, можно сделать отдельное перенаправление по роли
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'service_track_app/login.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    return redirect('home')


def tracking_view(request):
    return render(request, 'service_track_app/tracking.html')


def track_request_view(request):
    repair_request = None
    status_history = RequestHistory.objects.none()

    if request.method == 'POST':
        serial_number = request.POST.get('serial_number', '').strip().upper()

        if not serial_number:
            messages.error(request, "Пожалуйста, введите серийный номер.")
        else:
            try:
                repair_request = get_object_or_404(RepairRequest, serial_number__iexact=serial_number)
                # status_history = repair_request.history.order_by('changed_at')
                if repair_request:
                    # Берём только изменения статуса
                    status_history = repair_request.history.exclude(old_status=F('new_status')).order_by('changed_at')
            except:
                messages.error(request, f"Заявка с серийным номером {serial_number} не найдена.")
    print("!!!", status_history)
    for h in status_history:
        print(h.changed_at)  # теперь это работает

    return render(request, 'service_track_app/tracking.html', {"repair_request": repair_request, "status_history": status_history})


@login_required
@role_required(['dealer'])
def create_request_view(request):
    if request.method == "POST":
        # print("=== ДИАГНОСТИКА ФАЙЛОВ ===")
        # print("request.FILES:", dict(request.FILES))

        photos = request.FILES.getlist('photos')  # список загруженных файлов
        videos = request.FILES.getlist('videos')
        # print(f"Количество файлов в getlist('photos'): {len(photos)}")

        # for i, photo in enumerate(photos):
        #     print(f"Файл {i}: {photo.name} ({photo.size} bytes)")

        form = RepairRequestForm(request.POST, request.FILES)
        if form.is_valid():
            repair_request = form.save(commit=False)  # создаём объект, но не сохраняем
            repair_request.created_by = request.user  # автор заявки = текущий пользователь
            repair_request.dealer_company = request.user.dealer_company  # компания берётся у пользователя
            repair_request.save()  # теперь сохраняем в БД

            # Сохраняем фотографии
            for photo in photos:
                RepairRequestPhoto.objects.create(
                    repair_request=repair_request,
                    photo=photo
                )

            for video in videos:
                RepairRequestVideo.objects.create(
                    repair_request=repair_request,
                    video=video
                )

            # --- Создаём запись в истории сразу после создания ---
            RequestHistory.objects.create(
                repair_request=repair_request,
                changed_by=request.user,
                new_status='accepted_by_dealer',
                comment="Товар получен от покупателя и зарегистрирован в системе"
            )

            return redirect("my_requests")  # после создания переходим в "Мои заявки"
    else:
        form = RepairRequestForm()

    return render(request, "service_track_app/create.html", {"form": form})


@login_required
def my_requests_view(request):
    # if request.user.role == 'dealer':
    #     requests = RepairRequest.objects.filter(created_by=request.user, status__in=['in_progress', 'waiting'])
    # elif request.user.role == 'service_center':
    #     requests = RepairRequest.objects.filter(status__in=['in_progress', 'waiting'])
    #
    # # requests = RepairRequest.objects.order_by("-created_at")  # последние сверху
    # return render(request, "service_track_app/requests.html", {"requests": requests})
    if request.method == "POST":
        # Получаем список ID выбранных заявок из формы
        ids = request.POST.getlist("selected_requests")
        print('1'*50)
        print(ids)
        if ids:
            # Создаём новый пакет
            pkg = Package.objects.create(
                created_by=request.user,
                dealer_company=request.user.dealer_company  # если у пользователя есть дилерская компания
            )

            # # Обновляем статус и время отправки выбранных заявок
            # RepairRequest.objects.filter(id__in=ids).update(
            #     status='sent_to_service',
            #     sent_at=timezone.now()
            # )
            # Привязываем заявки к пакету и обновляем статус
            # RepairRequest.objects.filter(id__in=ids).update(
            #     status='sent_to_service',
            #     sent_at=timezone.now(),
            #     package=pkg
            # )

            # Получаем объекты заявок
            selected_requests = RepairRequest.objects.filter(id__in=ids)

            # Привязываем заявки к пакету и обновляем статус
            for repair_request in selected_requests:
                previous_status = repair_request.status  # сохраняем текущий статус перед изменением
                repair_request.status = 'sent_to_service'
                repair_request.sent_at = timezone.now()
                repair_request.package = pkg
                repair_request.save()

                # --- Создаём запись в истории ---
                RequestHistory.objects.create(
                    repair_request=repair_request,
                    changed_by=request.user,
                    old_status=previous_status,  # если нужно, можно сохранять предыдущий статус
                    new_status=repair_request.status,
                    comment="Отправлено в сервисный центр"
                )
            messages.success(request, f"Отправлено {len(ids)} заявок в сервисный центр.")
            remaining = RepairRequest.objects.filter(
                created_by=request.user,
                status__in=['in_progress', 'waiting']
            ).exists()
            url = reverse('my_requests') + '?sent=1&all_sent=' + ('0' if remaining else '1')
            return redirect(url)
        else:
            messages.warning(request, "Не выбрано ни одной заявки.")
        return redirect('my_requests')
    else:
        print('2' * 50)
        if request.user.role == 'dealer':
            requests = RepairRequest.objects.filter(created_by=request.user, status__in=['accepted_by_dealer', 'waiting'])
        elif request.user.role == 'service_center':
            requests = RepairRequest.objects.filter(status__in=['accepted_by_dealer', 'waiting'])

        # requests = RepairRequest.objects.order_by("-created_at")  # последние сверху
        return render(request, "service_track_app/requests.html", {"requests": requests})


# def sent_requests_view(request):
#     if request.method == "POST":
#         return redirect('sent_requests')
#     else:
#         if request.user.role == 'dealer':
#             # requests = RepairRequest.objects.filter(sent_at__isnull=False)
#             packages = Package.objects.filter(created_by=request.user)
#         elif request.user.role == 'service_center':
#             # requests = RepairRequest.objects.filter(sent_at__isnull=False)
#             packages = Package.objects.all()
#         else:
#             packages = Package.objects.none()
#
#         return render(request, "service_track_app/sent.html", {"packages": packages})
#     # return redirect('sent_requests')


# def sent_requests_view(request):
#     if request.method == "POST":
#         return redirect('sent_requests')
#     else:
#         status_filter = request.GET.get('status', 'all')
#
#         if request.user.role == 'dealer':
#             packages = Package.objects.filter(created_by=request.user)
#         elif request.user.role == 'service_center':
#             packages = Package.objects.all()
#         else:
#             packages = Package.objects.none()
#
#         # Фильтрация по статусу
#         if status_filter != 'all':
#             packages = packages.filter(status=status_filter)
#
#         packages = packages.order_by('-created_at')
#
#         return render(request, "service_track_app/sent.html", {
#             "packages": packages,
#             "current_status": status_filter
#         })


def sent_requests_view(request):
    if request.method == "POST":
        return redirect('sent_requests')
    else:
        status_filter = request.GET.get('status', 'all')

        if request.user.role == 'dealer':
            packages = Package.objects.filter(created_by=request.user)
        elif request.user.role == 'service_center':
            packages = Package.objects.all()
        else:
            packages = Package.objects.none()

        # Фильтрация по статусу
        if status_filter != 'all':
            packages = packages.filter(status=status_filter)

        # Предзагрузка связанных заявок с товарами
        packages = packages.prefetch_related('requests__product').order_by('-created_at')

        return render(request, "service_track_app/sent.html", {
            "packages": packages,
            "current_status": status_filter
        })


# @login_required
# @role_required(['service_center'])
# def received_requests_view(request):
#     packages = Package.objects.all()
#     # packages = Package.objects.prefetch_related('repairrequest_set').all()
#     repair_requests = RepairRequest.objects.filter(
#         sent_at__isnull=False,  # есть дата отправки
#         package__isnull=False,  # есть привязка к пакету
#         status='sent_to_service'  # статус "Отправлено в сервисный центр"
#     )
#
#     # Фильтрация по статусу поступления
#     # status = request.GET.get('status', 'all')  # Получаем статус из параметра GET
#     # if status != 'all':
#     #     repair_requests = RepairRequest.objects.filter(status=status)
#     # else:
#     #     repair_requests = RepairRequest.objects.filter(status__in=['received', 'inprogress', 'completed'])
#
#     return render(request, 'service_track_app/received2.html', {'packages': packages, 'repair_requests': repair_requests})


# @login_required
# @role_required(['service_center'])
# def received_requests_view(request):
#     if request.method == "POST":
#         return redirect('received_requests')
#     else:
#         status_filter = request.GET.get('status', 'all')
#
#         # Для СЦ показываем все пакеты
#         packages = Package.objects.all()
#
#         # Фильтрация по статусу
#         if status_filter != 'all':
#             packages = packages.filter(status=status_filter)
#
#         # Предзагрузка связанных заявок с товарами
#         packages = packages.prefetch_related('requests__product').order_by('-created_at')
#
#         return render(request, "service_track_app/received.html", {
#             "packages": packages,
#             "current_status": status_filter
#         })


@login_required
@role_required(['service_center'])
def received_requests(request):
    if request.method == "POST":
        return redirect('received_requests')
    else:
        status_filter = request.GET.get('status', 'all')
        view_type = request.GET.get('view', 'packages')  # Получаем тип view

        # Для СЦ показываем все пакеты
        packages = Package.objects.all()

        # Отдельные заявки (все заявки со статусом отправки в СЦ)
        repair_requests = RepairRequest.objects.filter(
            status='sent_to_service'
        ).select_related('product').order_by('-created_at')

        # Фильтрация пакетов по статусу
        if status_filter != 'all':
            packages = packages.filter(status=status_filter)

        # Предзагрузка связанных заявок с товарами
        packages = packages.prefetch_related('requests__product').order_by('-created_at')

        print('!!!!!!!!!!!!',view_type)

        return render(request, "service_track_app/received.html", {
            "packages": packages,
            "repair_requests": repair_requests,  # Добавляем отдельные заявки
            "current_status": status_filter,
            "show_requests": view_type == 'requests'  # Определяем какой вид показывать
        })


@login_required
def package_detail_view(request, package_id):
    # Получаем пакет или 404
    pkg = get_object_or_404(Package, id=package_id)

    user_role = request.user.role

    # Определяем, кто пользователь и куда вести "Назад"
    if user_role == 'dealer':
        back_url = reverse('sent_requests')
        back_title = "Отправленные пакеты"
    elif user_role == 'service_center':
        back_url = reverse('received_requests')
        back_title = "Поступившие пакеты"

    print(back_url)
    print(back_title)

    # Берём все заявки внутри пакета
    requests = pkg.requests.all().order_by('-sent_at')

    return render(request, "service_track_app/package_detail.html", {
        'p': pkg,
        'requests': requests,
        'back_url': back_url,
        'back_title': back_title,
    })


def sc_package_detail(request, package_id):
    package = get_object_or_404(Package, id=package_id)
    # requests = package.requests.all()
    requests = package.requests.all().prefetch_related('photos', 'videos')
    return render(request, 'service_track_app/sc_package_detail.html', {
        'p': package,
        'requests': requests
    })


def request_detail(request, request_id):
    repair_request = get_object_or_404(RepairRequest, id=request_id)
    user_role = request.user.role

    print("=== repair_request.package ===")
    print(repair_request.package)  # Сам объект пакета
    print(repair_request.package.id)  # ID пакета
    print(repair_request.package_id)  # Прямой ID (из БД)

    if user_role == 'dealer':
        back_url = reverse('package_detail', args=[repair_request.package.id])
        back_title = "пакету заявок"
        package_date = repair_request.package.created_at.strftime("%d.%m.%Y")
        breadcrumbs = [
            {'title': 'Отправленные', 'url': reverse('sent_requests')},
            {'title': f'Пакет от {package_date}', 'url': back_url},
            {'title': f'Заявка #{repair_request.id}', 'url': ''}
        ]
    elif user_role == 'service_center':
        if repair_request.package:
            back_url = reverse('sc_package_detail', args=[repair_request.package.id])
            back_title = "пакету заявок"
            package_date = repair_request.package.created_at.strftime("%d.%m.%Y")
            breadcrumbs = [
                {'title': 'Поступившие в СЦ', 'url': reverse('received_requests')},
                {'title': f'Пакет от {package_date}', 'url': back_url},
                {'title': f'Заявка #{repair_request.id}', 'url': ''}
            ]
        else:
            back_url = reverse('received_requests')
            back_title = "поступившим заявкам"

    if request.method == 'POST':
        form = RepairRequestEditForm(request.POST, instance=repair_request)
        if form.is_valid():
            # print("Форма валидна. Данные:", form.cleaned_data)  # Печатает данные, которые форма прошла валидацию
            # form.save()
            # print("Данные сохранены.")
            previous_status = RepairRequest.objects.get(id=repair_request.id).status

            updated_request = form.save(commit=False)
            updated_request.save()  # сохраняем изменения

            # создаём запись в истории
            RequestHistory.objects.create(
                repair_request=updated_request,
                changed_by=request.user,
                old_status=previous_status,
                new_status=updated_request.status,
                comment=updated_request.additional_notes  # или другое поле комментария
            )
            return redirect('request_detail', request_id=repair_request.id)
        else:
            print("Ошибки формы:", form.errors)
    else:
        form = RepairRequestEditForm(instance=repair_request)

    # Получаем все фото для этой заявки
    photos = repair_request.photos.all()  # если используется related_name='photos'
    videos = repair_request.videos.all()
    print('photos: ',photos)
    print('videos: ', videos)

    return render(request, 'service_track_app/request_detail.html', {
        'form': form,
        'repair_request': repair_request,
        'photos': photos,
        'videos': videos,
        'back_url': back_url,
        'back_title': back_title,
        'breadcrumbs': breadcrumbs
    })


def update_request_status(request, request_id):
    print('1'*20)
    if request.method == "POST":
        req = RepairRequest.objects.get(id=request_id)
        old_status = req.status
        new_status = request.POST.get("status")
        comment = request.POST.get("comment")

        if new_status != old_status or comment:
            RequestHistory.objects.create(
                repair_request=req,
                changed_by=request.user,
                old_status=old_status,
                new_status=new_status,
                comment=comment
            )

        req.status = new_status
        req.save()

        # После сохранения — редирект на страницу деталей заявки
        return redirect('request_detail', request_id=request_id)

    # Если кто-то зайдёт GET-запросом — можно вернуть ошибку или редирект
    return redirect('my_requests')


# def accept_selected_requests(request, package_id):
#     if request.method == 'POST':
#         selected_ids = request.POST.getlist('selected_requests')
#         package = get_object_or_404(Package, id=package_id)
#
#         if selected_ids:
#             for request_id in selected_ids:
#                 repair_request = RepairRequest.objects.get(id=request_id)
#                 old_status = repair_request.status
#                 print(old_status)
#                 repair_request.status = 'accepted_by_dealer'
#                 repair_request.save()
#
#                 RequestHistory.objects.create(
#                     repair_request=repair_request,
#                     changed_by=request.user,
#                     old_status=old_status,
#                     new_status='accepted_by_dealer',
#                     comment='Заявка принята в сервисном центре'
#                 )
#
#             # 🔥 ПРОВЕРЯЕМ ВСЕ ЛИ ЗАЯВКИ ПРИНЯТЫ
#             all_requests = package.requests.all()  # Все заявки пакета
#             accepted_requests = all_requests.filter(status='accepted_by_dealer')  # Принятые
#
#             total_count = all_requests.count()
#             accepted_count = accepted_requests.count()
#
#             # Если приняли ВСЕ заявки из пакета
#             if accepted_count == total_count:
#                 package.status = 'accepted'
#                 package.save()
#                 messages.success(request, f'Приняты все {accepted_count} заявок пакета! Статус пакета обновлен.')
#             else:
#                 # Приняли только часть заявок
#                 messages.success(request,
#                                  f'Принято {len(selected_ids)} заявок. В пакете осталось {total_count - accepted_count} не принятых.')
#
#         else:
#             messages.warning(request, 'Не выбрано ни одной заявки для принятия')
#
#         received_url = reverse('received_requests')
#         redirect_url = f"{received_url}?status=accepted&view=packages"
#
#         return redirect(redirect_url)

def accept_selected_requests(request, package_id):
    if request.method == 'POST':
        selected_ids = request.POST.getlist('selected_requests')
        package = get_object_or_404(Package, id=package_id)

        # Получаем все заявки в пакете
        all_requests_in_package = package.requests.all()
        all_request_ids = set(all_requests_in_package.values_list('id', flat=True))
        selected_ids_set = set(map(int, selected_ids)) if selected_ids else set()

        # Проверяем, выбраны ли ВСЕ заявки из пакета
        if selected_ids_set != all_request_ids:
            messages.error(request, 'Для принятия пакета необходимо выбрать ВСЕ заявки в пакете')
            return redirect('sc_package_detail', package_id=package_id)

        if selected_ids:
            for request_id in selected_ids:
                repair_request = RepairRequest.objects.get(id=request_id)
                old_status = repair_request.status
                repair_request.status = 'accepted_by_dealer'
                repair_request.save()

                RequestHistory.objects.create(
                    repair_request=repair_request,
                    changed_by=request.user,
                    old_status=old_status,
                    new_status='accepted_by_dealer',
                    comment='Заявка принята в сервисном центре'
                )

            # Проверяем все ли заявки приняты
            all_requests = package.requests.all()
            accepted_requests = all_requests.filter(status='accepted_by_dealer')

            total_count = all_requests.count()
            accepted_count = accepted_requests.count()

            # Если приняли ВСЕ заявки из пакета
            if accepted_count == total_count:
                package.status = 'accepted'
                package.save()
                messages.success(request, f'Приняты все {accepted_count} заявок пакета! Статус пакета обновлен.')
            else:
                messages.success(request, f'Принято {len(selected_ids)} заявок. В пакете осталось {total_count - accepted_count} не принятых.')

        else:
            messages.warning(request, 'Не выбрано ни одной заявки для принятия')

        return redirect('sc_package_detail', package_id=package_id)