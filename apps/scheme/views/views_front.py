from django.http import HttpResponse
from rest_framework import (viewsets, status, generics, filters, mixins)
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated

from apps.scheme.serializer.serializers_front import *
from rest_framework.response import Response
from rest_framework.decorators import action
from apps.scheme.pagination import SchemePagination
from django.http import JsonResponse
import json


class SchemeDetailViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """

    slist:相似方案列表
    diagram’：系统框图

    """
    queryset = Scheme.objects.all()
    serializer_class = SchemeSerializer
    pagination_class = SchemePagination

    def get_serializer_class(self):
        if self.action == 'diagram':
            return FrontSchemeDesignSerializer
        elif self.action == 'slist':
            return SimilarSchemeSerializer
        # elif self.action == 'master':
        #     return SchemeMasterSerializer
        # elif self.action =='similarBom':
        #     return SimilarBomSerializers
        else:
            return SchemeDetailPageSerializer

    @action(['get'], detail=True)
    def slist(self, request, *args, **kwargs):
        """相似方案列表"""
        try:
            scheme = self.kwargs['pk']
            queryset = SimilarScheme.objects.filter(scheme=int(scheme))

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Electron.DoesNotExist:
            return Response({}, status=status.HTTP_200_OK)

    @action(['get'], detail=True)
    def diagram(self, request, *args, **kwargs):
        """系统框图"""
        try:
            scheme = self.kwargs['pk']
            queryset = SchemeSystemDesign.objects.filter(scheme=int(scheme))
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Electron.DoesNotExist:
            return Response({}, status=status.HTTP_200_OK)

    @action(['get'], detail=True)
    def share(self, request, *args, **kwargs):
        """方案分享"""
        try:
            scheme = self.kwargs['pk']
            user = request.user

            return Response({}, status=status.HTTP_200_OK)
        except Electron.DoesNotExist:
            return Response({}, status=status.HTTP_200_OK)
    #
    # @action(['get'], detail=True)
    # def master(self,request, *args, **kwargs):
    #     """方案大师"""
    #     try:
    #         scheme = self.kwargs['pk']
    #         queryset = Scheme.objects.filter(scheme=int(scheme))
    #         serializer = self.get_serializer(queryset, many=True)
    #         return Response(serializer.data, status=status.HTTP_200_OK)
    #     except Electron.DoesNotExist:
    #         return Response({}, status=status.HTTP_200_OK)


# 个人方案创建
class NewSchemeViewSet(CreateAPIView, UpdateAPIView):
    # permission_classes = [IsAuthenticated]
    queryset = Scheme.objects.all()
    serializer_class = NewSchemeSerializer

    def update(self, request, *args, **kwargs):
        validated_data= request.data
        id = validated_data['id']
        title = validated_data['title']
        price = validated_data['price']
        category = validated_data['category'][len(validated_data['category'])-1]
        images = validated_data['images']
        videos = validated_data['videos']
        designs = validated_data['designs']
        electrons = validated_data['electrons']
        desc_specific = validated_data['desc_specific']
        source_code = validated_data['source_code']
        code_name= validated_data['code_name']
        contact_name = validated_data['contact_name']
        contact_tel = validated_data['contact_tel']
        enterprise = validated_data['enterprise']
        contact_qq = validated_data['contact_qq']
        contact_email = validated_data['contact_email']


        with transaction.atomic():
            save_id = transaction.savepoint()

            scheme = Scheme.objects.get(id=id)
            Scheme.objects.update(
                title=title,
                price=price,
                category=category,
                images=images,
                desc_specific=desc_specific,
                source_code=source_code,
                code_name = code_name,
                contact_name=contact_name,
                contact_tel=contact_tel,
                enterprise=enterprise,
                contact_qq=contact_qq,
                contact_email=contact_email,
            )
            if not scheme:
                transaction.savepoint_rollback(save_id)
                return Response({"message": "方案更新失败"},status=status.HTTP_400_BAD_REQUEST)

            if videos:
                for video in videos:
                    if not video['id']:
                        scheme_video = SchemeVideo.objects.create(
                            scheme=scheme,
                            url=video['url'],
                            is_primary=video['is_primary'],
                        )
                        if not scheme_video:
                            transaction.savepoint_rollback(save_id)
                            return Response({"message": "方案更新失败"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                SchemeVideo.objects.all().delete()


            id_list = []
            if designs:

                for design in designs:
                    if design['id']:
                        id_list.append(design['id'])
                    if design['id'] =='':
                        scheme_design = SchemeSystemDesign.objects.create(
                            scheme=scheme,
                            name=design['name'],
                            image=design['image'],
                        )
                        id_list.append(scheme_design.id)

                        if not scheme_design:
                            transaction.savepoint_rollback(save_id)
                            return Response({"message": "方案更新失败"}, status=status.HTTP_400_BAD_REQUEST)

            ids = SchemeSystemDesign.objects.all()

            for i in ids:
                if i.id  not in id_list:
                    SchemeSystemDesign.objects.get(id=i.id).delete()

            if electrons:
                for electron in electrons:
                    model_name = Electron.objects.get(model_name=electron['model_name'])
                    if electron['id']:
                        scheme_ele = SchemeElectron.objects.filter(id=electron['id']).update(
                            model_name=model_name.id,
                            model_des=electron['model_des'],
                        )
                    else:
                        scheme_ele=SchemeElectron.objects.create(
                        scheme=scheme,
                        model_name=model_name,
                        model_des=electron['model_des'],
                        is_key=electron['is_key'],
                        is_record=True,
                        create_at=datetime.now()
                    )

                    if not scheme_ele:
                        transaction.savepoint_rollback(save_id)
                        return Response({"message": "方案更新失败"},status=status.HTTP_400_BAD_REQUEST)
            transaction.savepoint_commit(save_id)
        return Response({"message": "方案更新成功"},status=status.HTTP_200_OK)


# 个人方案详情
class NewSchemeDetailViewSet(mixins.RetrieveModelMixin,
                             mixins.DestroyModelMixin,
                             mixins.ListModelMixin,
                             viewsets.GenericViewSet):
    # permission_classes = [IsAuthenticated]
    queryset = Scheme.objects.all()
    serializer_class = NewSchemeDetailSerializer
    pagination_class = SchemePagination

    # def get_queryset(self):
    #     queryset= Scheme.objects.filter(scheme_user=self.request.user)
    #     return queryset
    def get_serializer_class(self):
        if self.action == 'list':
            return NewSchemeListSerializer

        return NewSchemeDetailSerializer




# 方案分类
class NewSchemeCategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = NewSchemeCategorySerializer3
    queryset = SchemeCategory.objects.all()

    def list(self, request, *args, **kwargs):
        scheme_categories = SchemeCategory.objects.filter(parent=None)
        serializer = NewSchemeCategoryListSerializer(scheme_categories, many=True)
        for i, j in enumerate(serializer.data):
            if not serializer.data[i]['children']:
                serializer.data[i]['children'] = None
            else:
                for a, b in enumerate(serializer.data[i]['children']):
                    if not serializer.data[i]['children'][a]['children']:
                        serializer.data[i]['children'][a]['children'] = None

        return Response(serializer.data, status=status.HTTP_200_OK)


# 方案bom元器件
class SchemeBomElectronViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Electron.objects.all()
    serializer_class = SchemeElectronSerializer

    def list(self, request, *args, **kwargs):
        model_name = request.query_params['model_name']
        queryset = Electron.objects.filter(model_name__istartswith=model_name)
        serializer = SchemeElectronSerializer(queryset, many=True)

        return Response(serializer.data[:10], status.HTTP_200_OK)


class SchemeElectronDeleteViewset(mixins.DestroyModelMixin, viewsets.GenericViewSet):
    # permission_classes = [IsAuthenticated]
    queryset = SchemeElectron.objects.all()
    serializer_class = NewSchemeElectronSerializer



