import json

from django.http import JsonResponse
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from rasweb.mailing import sendMail
from .models import *
from .serializer import InventorySerializer, ReserveSerializer, ScheduleSerializer


class InventoryListApi(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = InventorySerializer
    model = Inventory

    def get_queryset(self):
        return Inventory.objects.filter(code__icontains=self.request.GET["code"]).order_by("-code")


class ItemDetailApi(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = InventorySerializer
    model = Inventory

    def get_queryset(self):
        return Inventory.objects.filter(code__icontains=self.request.GET["code"]).order_by("-code")


class ReserveListApi(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        query_list = []
        date = request.GET["date"]
        code = request.GET["code"]
        name = request.GET["name"]
        reservations = self.get_queryset(params=[date, name, code])
        for reservation in reservations:
            query_list.append(reservation.serializer())
        return JsonResponse(query_list, safe=False)

    def get_queryset(self, **kwargs):
        params = kwargs["params"]
        return Reserve.objects.filter(
            element__name__icontains=params[1],
            element__code=params[2]
        ).exclude(schedule__date_start__lt=params[0],
                  schedule__date_end__lt=params[0]).order_by("-element__code")


class CreateReservationApi(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.data)
        schedule = data["schedule"]
        element = data["element"]
        user = data["user"]

        schedule_record, element_in_db, user_in_db, reservation = None, None, None, None
        if len(schedule["date"]) == 1:
            date_start, date_end = schedule["date"][0], schedule["date"][0]
        else:
            date_start, date_end = schedule["date"][0], schedule["date"][1]
        try:
            schedule_record = Schedule.objects.get(
                date_start=date_start,
                date_end=date_end,
                start_time=schedule["start"],
                end_time=schedule["end"]
            )
        except Schedule.DoesNotExist:
            schedule_record = Schedule.objects.create(
                date_start=date_start,
                date_end=date_end,
                start_time=schedule["start"],
                end_time=schedule["end"]
            )
        try:
            element_in_db = Inventory.objects.get(
                name=element["name"],
                code=element["code"]
            )
        except Inventory.DoesNotExist:
            pass
        try:
            user_in_db = User.objects.get(username=user["username"])
        except User.DoesNotExists:
            pass
        reservation = Reserve.objects.create(
            user=user_in_db,
            schedule=schedule_record,
            element=element_in_db,
            quantity=element_in_db.quantity,
        )
        self.mail_configs(reservation)
        try:
            return JsonResponse({'created': True})
        except:
            return JsonResponse({'created': False})

    def mail_configs(self, reservation):
        username = reservation.user.username
        subject = '{0} {1}, reservaste el elemento {2} en la ubicación {3}'.format(
            reservation.user.first_name,
            reservation.user.last_name,
            reservation.element.name,
            reservation.element.code
        )
        try:
            date_formatted = reservation.schedule.date_start.strftime("%d de %b. de %Y")
            start_formatted = reservation.schedule.start_time.strftime("%I :%M %p")
            end_formatted = reservation.schedule.end_time.strftime("%I:%M %p")
        except:
            date_formatted = datetime.strptime(reservation.schedule.date_start, '%Y-%m-%d').strftime("%d de %b. de %Y")
            start_formatted = str(reservation.schedule.start_time)[0:len(str(reservation.schedule.start_time)) - 3]
            end_formatted = str(reservation.schedule.end_time)[0:len(str(reservation.schedule.start_time)) - 3]

        description = 'Descarga el archivo con formato .ics y sincroniza tu calendario con la reserva que tienes el {0}' \
                      ' de {1} a {2}'.format(date_formatted, start_formatted, end_formatted)
        context = {
            'username': username,
            'subject': subject,
            'description': description
        }
        configs = {
            'Template': 'MailTemplates/reservation-mail.html',
            'subject': 'Detalles de tu reserva',
            'to': [reservation.user.email],
        }
        file_configs = {
            'file_name': '{0}_reservation.ics'.format(reservation.user.first_name),
            'content': reservation.generate_event(),
            'type': 'text/calendar'
        }
        sendMail(configs, context, file_configs)


class ElementInfoApi(generics.RetrieveAPIView):
    serializer_class = InventorySerializer

    def get_queryset(self):
        return Inventory.objects.filter(pk=self.kwargs['pk'])


class ScheduleInfoApi(generics.RetrieveAPIView):
    serializer_class = ScheduleSerializer
    model = Schedule

    def get_queryset(self):
        return Schedule.objects.filter(pk=self.kwargs['pk'])


class ReservationHistoryApi(generics.ListAPIView):
    model = Reserve
    serializer_class = ReserveSerializer

    def get_queryset(self):
        query = self.request.GET.get("query")
        date_start = self.request.GET.get("dateStart")
        date_end = self.request.GET.get("dateEnd")
        return Reserve.objects.filter(element__name__icontains=query, schedule__date_start__gte=date_start,
                                      schedule__date_end__lte=date_end).order_by('-schedule__date_start')
