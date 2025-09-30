from django.shortcuts import render, redirect, get_object_or_404
from .forms import RepairRequestForm
from .models import RepairRequest


def tracking_view(request):
    return render(request, 'service_track_app/tracking.html')

# @login_required
# @role_required(['dealer'])
def create_request_view(request):
    if request.method == "POST":
        form = RepairRequestForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("my_requests")  # после создания переходим в "Мои заявки"
    else:
        form = RepairRequestForm()

    return render(request, "service_track_app/create.html", {"form": form})


def my_requests_view(request):
    requests = RepairRequest.objects.order_by("-created_at")  # последние сверху
    return render(request, "service_track_app/requests.html", {"requests": requests})


def sent_requests_view(request):
    return render(request, 'service_track_app/sent.html')


def received_view(request):
    # Фильтрация по статусу поступления
    status = request.GET.get('status', 'all')  # Получаем статус из параметра GET
    if status != 'all':
        repair_requests = RepairRequest.objects.filter(status=status)
    else:
        repair_requests = RepairRequest.objects.filter(status__in=['received', 'inprogress', 'completed'])

    return render(request, 'service_track_app/received.html', {'repair_requests': repair_requests})

def request_detail(request, request_id):
    # Получаем объект заявки по id
    repair_request = get_object_or_404(RepairRequest, id=request_id)
    print(repair_request)

    if request.method == 'POST':
        print("!!", request.POST)
        form = RepairRequestForm(request.POST, instance=repair_request)
        if form.is_valid():
            print("Форма валидна. Данные:", form.cleaned_data)  # Печатает данные, которые форма прошла валидацию
            form.save()
            print("Данные сохранены.")
            return redirect('request_detail', request_id=repair_request.id)
        else:
            print("Ошибки формы:", form.errors)
    else:
        form = RepairRequestForm(instance=repair_request)

    return render(request, 'service_track_app/request_detail.html', {'form': form, 'repair_request': repair_request})