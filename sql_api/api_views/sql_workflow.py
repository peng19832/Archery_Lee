# -*- coding: UTF-8 -*-
""" 
@author: hhyo
@license: Apache Licence
@file: api_sql_workflow.py
@time: 2022/10/07
"""
__author__ = "hhyo"

from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator
from drf_spectacular.utils import extend_schema
from rest_framework import views, permissions, serializers
from rest_framework.response import Response

from sql.engines import get_engine
from sql_api.serializers.sql_workflow import (
    ExecuteCheckSerializer,
    ExecuteCheckResultSerializer,
)


class ExecuteCheck(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="SQL检查",
        request=ExecuteCheckSerializer,
        responses={200: ExecuteCheckResultSerializer},
        description="对提供的SQL进行语法检查",
    )
    @method_decorator(permission_required("sql.sql_submit", raise_exception=True))
    def post(self, request):
        # 参数验证
        serializer = ExecuteCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.get_instance()
        # 交给engine进行检测
        try:
            check_engine = get_engine(instance=instance)
            check_result = check_engine.execute_check(
                db_name=request.data["db_name"], sql=request.data["full_sql"].strip()
            )
        except Exception as e:
            raise serializers.ValidationError({"errors": f"{e}"})
        check_result.rows = check_result.to_dict()
        serializer_obj = ExecuteCheckResultSerializer(check_result)
        return Response(serializer_obj.data)
