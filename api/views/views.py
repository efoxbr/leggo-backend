from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
from rest_framework import serializers, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from api.models import (
    EtapaProposicao, TemperaturaHistorico, InfoGerais, Progresso, Proposicao,
    Comissao, PautaHistorico, Emendas)
from datetime import datetime
from api.utils.filters import get_time_filtered_temperatura, get_time_filtered_pauta


class TemperaturaHistoricoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemperaturaHistorico
        fields = ('periodo', 'temperatura_recente', 'temperatura_periodo')


class ComissaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comissao
        fields = (
            'cargo', 'id_parlamentar', 'partido', 'uf', 'situacao',
            'nome', 'foto', 'sigla', 'casa')


class PautaHistoricoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PautaHistorico
        fields = ('data', 'semana', 'local', 'em_pauta')


class EtapasSerializer(serializers.ModelSerializer):
    temperatura_historico = TemperaturaHistoricoSerializer(many=True, read_only=True)
    pauta_historico = PautaHistoricoSerializer(many=True, read_only=True)

    class Meta:
        model = EtapaProposicao
        fields = (
            'id', 'id_ext', 'casa', 'sigla', 'data_apresentacao', 'ano', 'sigla_tipo',
            'regime_tramitacao', 'forma_apreciacao', 'ementa', 'justificativa', 'url',
            'temperatura_historico', 'autor_nome', 'relator_nome', 'casa_origem',
            'em_pauta', 'apelido', 'tema', 'status', 'resumo_tramitacao',
            'temperatura_coeficiente', 'pauta_historico')


class ProposicaoSerializer(serializers.ModelSerializer):
    etapas = EtapasSerializer(many=True, read_only=True)

    class Meta:
        model = Proposicao
        fields = ('id', 'tema', 'apelido', 'etapas', 'resumo_progresso')


class ProgressoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Progresso
        fields = ('fase_global', 'local', 'data_inicio',
                  'data_fim', 'local_casa', 'pulou')


class EmendasSerialzer(serializers.ModelSerializer):
    class Meta:
        model = Emendas
        fields = ('data_apresentacao', 'local', 'autor')


class Info(APIView):
    '''
    Informações gerais sobre a plataforma.
    '''

    def get(self, request, format=None):
        return Response({i.name: i.value for i in InfoGerais.objects.all()})


class EtapasList(generics.ListAPIView):
    '''
    Dados gerais da proposição.
    '''
    queryset = EtapaProposicao.objects.prefetch_related(
        'tramitacao', 'temperatura_historico')
    serializer_class = EtapasSerializer


class ProposicaoList(generics.ListAPIView):
    '''
    Lista de proposições e seus dados gerais.
    '''
    serializer_class = ProposicaoSerializer

    def get_queryset(self):
        temperaturaQs = get_time_filtered_temperatura(self.request)
        pautaQs = get_time_filtered_pauta(self.request)
        return Proposicao.objects.prefetch_related(
            'etapas', 'etapas__tramitacao', 'progresso',
            Prefetch('etapas__temperatura_historico', queryset=temperaturaQs),
            Prefetch('etapas__pauta_historico', queryset=pautaQs),
        )


# class TemperaturaHistoricoAPI(APIView):
#     '''
#     Historico de temperaturas de uma proposicao
#     '''
#     @swagger_auto_schema(
#         manual_parameters=[
#             openapi.Parameter(
#                 'casa', openapi.IN_PATH,
#                 'casa da proposição', type=openapi.TYPE_STRING),
#             openapi.Parameter(
#                 'id_ext', openapi.IN_PATH, 'id da proposição no sistema da casa',
#                 type=openapi.TYPE_INTEGER),
#             openapi.Parameter(
#                 'semanas_anteriores', openapi.IN_PATH,
#                 'número de semanas anteriores a retornar',
#                 type=openapi.TYPE_INTEGER),
#             openapi.Parameter(
#                 'data_referencia', openapi.IN_PATH,
#                 'data de referência a ser considerada',
#                 type=openapi.TYPE_STRING),
#         ]
#     )
#     def get(self, request, casa=None, id_ext=None):
#         '''
#         Retorna o histórico de temperaturas de uma proposição, retornando a quantidade
#         especificada de semanas anteriores à data de referência.
#         '''
#         queryset = get_time_filtered_temperatura(request).filter(
#             proposicao__casa=casa, proposicao__id_ext=id_ext)

#         temperaturas = [TemperaturaHistoricoSerializer(temperatura).data
#                         for temperatura in queryset]

#         return Response({
#             'coeficiente': get_coefficient_temperature(queryset),
#             'temperaturas': temperaturas
#         })


class ProgressoList(generics.ListAPIView):
    '''
    Dados do progresso da proposição por período, de acordo com uma data de referência.
    '''
    serializer_class = ProgressoSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'casa', openapi.IN_PATH, 'casa da proposição', type=openapi.TYPE_STRING),
            openapi.Parameter(
                'id_ext', openapi.IN_PATH, 'id da proposição no sistema da casa',
                type=openapi.TYPE_INTEGER),
            openapi.Parameter(
                'data_referencia', openapi.IN_PATH,
                'data de referência a ser considerada',
                type=openapi.TYPE_STRING),
        ]
    )
    def get_queryset(self):
        '''
        Retorna o progresso de uma proposição, passando uma data de referência.
        '''
        casa = self.kwargs['casa']
        id_ext = self.kwargs['id_ext']
        data_referencia = self.request.query_params.get('data_referencia', None)
        queryset = Progresso.objects.filter(
            etapa__casa=casa, etapa__id_ext=id_ext)

        try:
            hoje = datetime.today() if data_referencia is None else datetime.strptime(
                data_referencia, '%Y-%m-%d')
        except ValueError:
            print(
                f'Data de referência ({data_referencia}) inválida. '
                'Utilizando data atual como data de referência.')
            hoje = datetime.today()

        if data_referencia is None:
            queryset = queryset.filter()
        else:
            queryset = queryset.filter(data_inicio__lte=hoje)

        return queryset


class ComissaoList(generics.ListAPIView):
    '''
    Dados da composição de uma comissão
    '''
    serializer_class = ComissaoSerializer

    def get_queryset(self):
        '''
        Retorna a comissao filtrada
        '''
        casa_parametro = self.kwargs['casa']
        sigla_parametro = self.kwargs['sigla']
        return Comissao.objects.filter(
            casa=casa_parametro, sigla=str.upper(sigla_parametro))


class PautaList(generics.ListAPIView):
    '''
    Dados do progresso da proposição por periodo de acordo com uma data de referência.
    '''

    serializer_class = PautaHistoricoSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'casa', openapi.IN_PATH, 'casa da proposição', type=openapi.TYPE_STRING),
            openapi.Parameter(
                'id_ext', openapi.IN_PATH, 'id da proposição no sistema da casa',
                type=openapi.TYPE_INTEGER),
            openapi.Parameter(
                'data_referencia', openapi.IN_PATH,
                'data de referência a ser considerada',
                type=openapi.TYPE_STRING),
        ]
    )
    def get_queryset(self):
        '''
        Retorna o histórico da pauta
        '''
        casa = self.kwargs['casa']
        id_ext = self.kwargs['id_ext']
        return get_time_filtered_pauta.filter(
            proposicao__casa=casa, proposicao__id_ext=id_ext)


class ProposicaoDetail(APIView):
    '''
    Detalha proposição.
    '''
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'casa', openapi.IN_PATH, 'casa da proposição', type=openapi.TYPE_STRING),
            openapi.Parameter(
                'id_ext', openapi.IN_PATH, 'id da proposição no sistema da casa',
                type=openapi.TYPE_INTEGER),
        ]
    )
    def get(self, request, casa, id_ext, format=None):
        prop = get_object_or_404(EtapaProposicao, casa=casa, id_ext=id_ext)
        return Response(EtapasSerializer(prop).data)


class EmendasList(generics.ListAPIView):
    '''
    Dados da emenda de uma proposição
    '''

    serializer_class = EmendasSerialzer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'casa', openapi.IN_PATH, 'casa da proposição', type=openapi.TYPE_STRING),
            openapi.Parameter(
                'id_ext', openapi.IN_PATH, 'id da proposição no sistema da casa',
                type=openapi.TYPE_INTEGER),
        ]
    )
    def get_queryset(self):
        '''
        Retorna a emenda
        '''
        casa = self.kwargs['casa']
        id_ext = self.kwargs['id_ext']
        queryset = Emendas.objects.filter(
            proposicao__casa=casa, proposicao__id_ext=id_ext)

        return queryset
