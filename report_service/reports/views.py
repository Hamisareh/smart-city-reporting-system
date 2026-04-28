# report_service/reports/views.py

from rest_framework import viewsets, status
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count
import logging

from .models import Report, Category, StatusHistory
from .serializers import ReportSerializer, CategorySerializer, StatusHistorySerializer
from .rabbitmq import send_notification

logger = logging.getLogger(__name__)


class IsAdminOrOwner(BasePermission):
    def has_permission(self, request, view):
        user_id = getattr(request, 'user_id', None)
        return user_id is not None

    def has_object_permission(self, request, view, obj):
        user_role = getattr(request, 'user_role', 'user')
        user_id = getattr(request, 'user_id', None)
        if user_role in ['admin', 'superadmin']:
            return True
        return obj.user_id == user_id


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        user_id = getattr(request, 'user_id', None)
        if user_id is None:
            return False
        if request.method in SAFE_METHODS:
            return True
        user_role = getattr(request, 'user_role', 'user')
        return user_role in ['admin', 'superadmin']


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAdminOrOwner]

    def get_queryset(self):
        user_id = getattr(self.request, 'user_id', None)
        user_role = getattr(self.request, 'user_role', 'user')

        if user_id is None:
            return Report.objects.none()

        if user_role in ['admin', 'superadmin']:
            return Report.objects.all().order_by('-created_at')

        return Report.objects.filter(user_id=user_id).order_by('-created_at')

    def perform_create(self, serializer):
        user_id = getattr(self.request, 'user_id', None)
        report = serializer.save(user_id=user_id)

        # ✅ إشعار للمستخدم اللي خلق التقرير
        send_notification(
            user_id=user_id,
            report_id=report.id,
            notification_type="REPORT_CREATED",
            is_for_admin=False
        )

        # ✅ إشعار لجميع المشرفين (admins)
        self._notify_admins(report.id, "NEW_REPORT_CREATED")

    def _notify_admins(self, report_id, notification_type):
        """إرسال إشعار لجميع المشرفين"""
        try:
            import requests
            response = requests.get('http://auth-service:8000/api/admins/', timeout=3)
            if response.ok:
                admins = response.json()
                for admin in admins:
                    send_notification(
                        user_id=admin['id'],
                        report_id=report_id,
                        notification_type=notification_type,
                        is_for_admin=True
                    )
                logger.info(f"✅ Notified {len(admins)} admins about report {report_id}")
        except Exception as e:
            logger.warning(f"⚠️ Could not notify admins: {e}")

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        old_status = instance.status
        user_role = getattr(request, 'user_role', 'user')

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        new_status = serializer.instance.status
        if old_status != new_status:
            StatusHistory.objects.create(
                report=instance,
                old_status=old_status,
                new_status=new_status
            )
            logger.info(f"Status changed: report {instance.id} : {old_status} to {new_status}")

            # ✅ إشعار للمستخدم صاحب التقرير فقط (مش للمشرفين)
            send_notification(
                user_id=instance.user_id,
                report_id=instance.id,
                notification_type="REPORT_STATUS_CHANGED",
                new_status=new_status,
                is_for_admin=False
            )

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    @action(detail=False, methods=['get'])
    def my_reports(self, request):
        reports = self.get_queryset()
        serializer = self.get_serializer(reports, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        user_id = getattr(request, 'user_id', None)
        user_role = getattr(request, 'user_role', 'user')

        if not user_id:
            return Response({'error': 'Non authentifie'}, status=401)

        if user_role in ['admin', 'superadmin']:
            reports_qs = Report.objects.all()
        else:
            reports_qs = Report.objects.filter(user_id=user_id)

        stats = reports_qs.values('status').annotate(count=Count('status'))

        result = {
            'total': reports_qs.count(),
            'pending': 0,
            'in_progress': 0,
            'resolved': 0
        }

        for stat in stats:
            if stat['status'] == 'pending':
                result['pending'] = stat['count']
            elif stat['status'] == 'in_progress':
                result['in_progress'] = stat['count']
            elif stat['status'] == 'resolved':
                result['resolved'] = stat['count']

        return Response(result)

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        report = self.get_object()
        history = report.history.all().order_by('-changed_at')
        serializer = StatusHistorySerializer(history, many=True)
        return Response(serializer.data)