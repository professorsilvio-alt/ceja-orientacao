from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import Usuario
from orientador_ia.models import DocumentoCerebro, FragmentoConhecimento, ConversaCerebro, MensagemCerebro
from orientador_ia.servicos_ia import buscar_contexto_relevante, gerar_resposta_beth


class OrientadorIaTest(TestCase):
    def setUp(self):
        # Usuário Diretor
        self.diretor = Usuario.objects.create_user(
            cpf='11122233344',
            nome_completo='Diretor Silva',
            email='diretor@ceja.rj.gov.br',
            perfil='diretor',
            password='SenhaForte123@'
        )

        # Usuário Professor (Não-Diretor)
        self.professor = Usuario.objects.create_user(
            cpf='55566677788',
            nome_completo='Professora Maria',
            email='maria@ceja.rj.gov.br',
            perfil='professor',
            password='SenhaForte123@'
        )

        self.client = Client()

    def test_controle_acesso_exclusivo_diretor(self):
        """Verifica se usuários não-diretores são bloqueados e diretores têm acesso."""
        url_chat = reverse('cerebro_chat')

        # Não autenticado -> Redireciona para login
        resp = self.client.get(url_chat)
        self.assertEqual(resp.status_code, 302)

        # Autenticado como Professor -> Redireciona com bloqueio
        self.client.force_login(self.professor)
        resp_prof = self.client.get(url_chat)
        self.assertEqual(resp_prof.status_code, 302)

        # Autenticado como Diretor -> Acesso permitido (200)
        self.client.force_login(self.diretor)
        resp_dir = self.client.get(url_chat)
        self.assertEqual(resp_dir.status_code, 200)

    def test_substituicao_automatica_normativas(self):
        """Verifica se a inclusão de uma norma mais nova revoga/substitui a anterior automaticamente."""
        # 1. Criar Normativa Antiga
        doc_antigo = DocumentoCerebro.objects.create(
            titulo='Normativa de Avaliação 01/2025',
            numero_normativa='01/2025',
            categoria='pedagogico',
            conteudo_extraido='A nota mínima para aprovação no módulo é 5.0.',
            status='vigente',
            criado_por=self.diretor
        )
        self.assertEqual(doc_antigo.status, 'vigente')

        # 2. Criar Normativa Nova que substitui a 01/2025
        doc_novo = DocumentoCerebro.objects.create(
            titulo='Normativa de Avaliação 02/2026',
            numero_normativa='02/2026',
            categoria='pedagogico',
            conteudo_extraido='A nota mínima para aprovação no módulo foi alterada para 6.0.',
            status='vigente',
            documento_substituido=doc_antigo,
            criado_por=self.diretor
        )

        # Recarregar doc antigo do banco
        doc_antigo.refresh_from_db()
        self.assertEqual(doc_antigo.status, 'substituido')
        self.assertEqual(doc_novo.status, 'vigente')

        # Verificar recuperação RAG (prioriza a vigente)
        contexto, fontes = buscar_contexto_relevante('Qual a nota mínima de aprovação?')
        self.assertIn('02/2026', contexto)
        self.assertIn('REVOGADO/SUBSTITUÍDO', contexto)

    def test_chat_api_envio_mensagem(self):
        """Testa endpoint de chat com a Beth."""
        self.client.force_login(self.diretor)
        conversa = ConversaCerebro.objects.create(usuario=self.diretor, titulo='Dúvida sobre Horário')

        payload = {
            'conversa_id': conversa.id,
            'mensagem': 'Qual é o horário de atendimento da secretaria?',
            'tipo_entrada': 'texto'
        }

        resp = self.client.post(
            reverse('cerebro_api_enviar_mensagem'),
            data=payload,
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['sucesso'])
        self.assertTrue(len(data['resposta']) > 0)
        self.assertEqual(conversa.mensagens.count(), 2)  # 1 pergunta diretor + 1 resposta beth
