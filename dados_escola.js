/**
 * dados_escola.js
 * Arquivo de configuração do CEJA Professora Rosa Soares
 * Edite este arquivo para atualizar os dados exibidos no totem.
 */

const DADOS_ESCOLA = {

  // ============================================================
  // HORÁRIO DOS PROFESSORES
  // ============================================================
  horarioProfessores: [
    {
      nome: "Prof. Leandro",
      // Para adicionar a foto, basta incluir o link da imagem na propriedade "foto" abaixo:
      foto: "", 
      disciplinas: ["Matemática"],
      horarios: [
        { dia: "Segunda-feira", inicio: "08:50", fim: "18:00", local: "Cabine de Matemática" },
        { dia: "Terça-feira", inicio: "08:50", fim: "13:00", local: "Cabine de Matemática" },
        { dia: "Quarta-feira", inicio: "14:40", fim: "18:00", local: "Cabine de Matemática" }
      ]
    },
    {
      nome: "Prof. Jordan",
      disciplinas: ["Matemática"],
      horarios: [
        { dia: "Segunda-feira", inicio: "16:20", fim: "20:30", local: "Cabine de Matemática" },
        { dia: "Terça-feira", inicio: "13:00", fim: "20:30", local: "Cabine de Matemática" },
        { dia: "Quarta-feira", inicio: "17:10", fim: "20:30", local: "Cabine de Matemática" },
        { dia: "Quinta-feira", inicio: "16:20", fim: "18:00", local: "Cabine de Matemática" }
      ]
    },
    {
      nome: "Prof. Arlindo",
      disciplinas: ["Matemática"],
      horarios: [
        { dia: "Quarta-feira", inicio: "08:50", fim: "17:10", local: "Cabine de Matemática" },
        { dia: "Quinta-feira", inicio: "08:50", fim: "20:30", local: "Cabine de Matemática" }
      ]
    },
    {
      nome: "Prof. Vitor",
      disciplinas: ["Matemática"],
      horarios: [
        { dia: "Terça-feira", inicio: "18:00", fim: "20:30", local: "Cabine de Matemática" },
        { dia: "Sexta-feira", inicio: "08:50", fim: "17:10", local: "Cabine de Matemática" }
      ]
    },
    {
      nome: "Profª Sandra",
      disciplinas: ["Português"],
      horarios: [
        { dia: "Terça-feira", inicio: "08:50", fim: "13:50", local: "Cabine de Linguagens" },
        { dia: "Quinta-feira", inicio: "08:50", fim: "13:50", local: "Cabine de Linguagens" }
      ]
    },
    {
      nome: "Profª Luciana Cavalcante",
      disciplinas: ["Português"],
      horarios: [
        { dia: "Terça-feira", inicio: "12:10", fim: "20:30", local: "Cabine de Linguagens" },
        { dia: "Quinta-feira", inicio: "18:50", fim: "20:30", local: "Cabine de Linguagens" }
      ]
    },
    {
      nome: "Profª Daniela",
      disciplinas: ["Português"],
      horarios: [
        { dia: "Quarta-feira", inicio: "13:50", fim: "18:50", local: "Cabine de Linguagens" },
        { dia: "Quinta-feira", inicio: "13:50", fim: "20:30", local: "Cabine de Linguagens" },
        { dia: "Sexta-feira", inicio: "08:50", fim: "17:10", local: "Cabine de Linguagens" }
      ]
    },
    {
      nome: "Prof. Rafael Souza",
      disciplinas: ["Espanhol"],
      horarios: [
        { dia: "Segunda-feira", inicio: "13:50", fim: "19:40", local: "Cabine de Linguagens" },
        { dia: "Terça-feira", inicio: "08:50", fim: "13:00", local: "Cabine de Linguagens" }
      ]
    },
    {
      nome: "Profª Luciana",
      disciplinas: ["Inglês"],
      horarios: [
        { dia: "Segunda-feira", inicio: "14:40", fim: "20:30", local: "Cabine de Linguagens" },
        { dia: "Quinta-feira", inicio: "14:40", fim: "18:50", local: "Cabine de Linguagens" }
      ]
    },
    {
      nome: "Prof. Wanderley",
      disciplinas: ["Inglês"],
      horarios: [
        { dia: "Quarta-feira", inicio: "10:30", fim: "16:20", local: "Cabine de Linguagens" },
        { dia: "Sexta-feira", inicio: "12:10", fim: "16:20", local: "Cabine de Linguagens" }
      ]
    },
    {
      nome: "Prof. Thalles",
      disciplinas: ["Educação Artística"],
      horarios: [
        { dia: "Terça-feira", inicio: "14:40", fim: "20:30", local: "Cabine de Linguagens" },
        { dia: "Sexta-feira", inicio: "08:50", fim: "13:00", local: "Cabine de Linguagens" }
      ]
    },
    {
      nome: "Profª Eliane",
      disciplinas: ["Educação Física"],
      horarios: [
        { dia: "Terça-feira", inicio: "15:30", fim: "20:30", local: "Cabine de Linguagens" },
        { dia: "Quinta-feira", inicio: "11:20", fim: "16:20", local: "Cabine de Linguagens" }
      ]
    },
    {
      nome: "Profª Viviane",
      disciplinas: ["Química"],
      horarios: [
        { dia: "Segunda-feira", inicio: "08:50", fim: "13:50", local: "Cabine de Ciências da Natureza" },
        { dia: "Terça-feira", inicio: "08:50", fim: "13:50", local: "Cabine de Ciências da Natureza" },
        { dia: "Quinta-feira", inicio: "08:50", fim: "12:10", local: "Cabine de Ciências da Natureza" },
        { dia: "Sexta-feira", inicio: "08:50", fim: "12:10", local: "Cabine de Ciências da Natureza" }
      ]
    },
    {
      nome: "Profª Marcela",
      disciplinas: ["Química"],
      horarios: [
        { dia: "Quarta-feira", inicio: "08:50", fim: "13:50", local: "Cabine de Ciências da Natureza" }
      ]
    },
    {
      nome: "Profª Alessandra",
      disciplinas: ["Ciências", "Biologia", "Química"],
      horarios: [
        { dia: "Segunda-feira", inicio: "12:10", fim: "20:30", local: "Cabine de Ciências da Natureza" },
        { dia: "Terça-feira", inicio: "08:50", fim: "13:00", local: "Cabine de Ciências da Natureza" },
        { dia: "Quinta-feira", inicio: "13:00", fim: "17:10", local: "Cabine de Ciências da Natureza" }
      ]
    },
    {
      nome: "Profª Delma",
      disciplinas: ["Ciências", "Biologia"],
      horarios: [
        { dia: "Terça-feira", inicio: "15:30", fim: "20:30", local: "Cabine de Ciências da Natureza" },
        { dia: "Quarta-feira", inicio: "15:30", fim: "20:30", local: "Cabine de Ciências da Natureza" }
      ]
    },
    {
      nome: "Prof. Elázaro",
      disciplinas: ["Ciências", "Biologia"],
      horarios: [
        { dia: "Quinta-feira", inicio: "08:50", fim: "12:10", local: "Cabine de Ciências da Natureza" },
        { dia: "Sexta-feira", inicio: "08:50", fim: "15:30", local: "Cabine de Ciências da Natureza" }
      ]
    },
    {
      nome: "Prof. Leonardo",
      disciplinas: ["Física"],
      horarios: [
        { dia: "Terça-feira", inicio: "08:50", fim: "14:40", local: "Cabine de Ciências da Natureza" },
        { dia: "Quarta-feira", inicio: "08:50", fim: "14:40", local: "Cabine de Ciências da Natureza" },
        { dia: "Quinta-feira", inicio: "08:50", fim: "13:50", local: "Cabine de Ciências da Natureza" }
      ]
    },
    {
      nome: "Prof. Xunei",
      disciplinas: ["Física"],
      horarios: [
        { dia: "Terça-feira", inicio: "14:40", fim: "19:40", local: "Cabine de Ciências da Natureza" },
        { dia: "Quarta-feira", inicio: "15:30", fim: "20:30", local: "Cabine de Ciências da Natureza" }
      ]
    },
    {
      nome: "Prof. Mário",
      disciplinas: ["História"],
      horarios: [
        { dia: "Segunda-feira", inicio: "13:50", fim: "20:30", local: "Cabine de Ciências Humanas" },
        { dia: "Sexta-feira", inicio: "13:50", fim: "17:10", local: "Cabine de Ciências Humanas" }
      ]
    },
    {
      nome: "Prof. Carlos Laurindo",
      disciplinas: ["História"],
      horarios: [
        { dia: "Terça-feira", inicio: "12:10", fim: "17:10", local: "Cabine de Ciências Humanas" },
        { dia: "Quinta-feira", inicio: "12:10", fim: "17:10", local: "Cabine de Ciências Humanas" }
      ]
    },
    {
      nome: "Profª Fabiane",
      disciplinas: ["História"],
      horarios: [
        { dia: "Quarta-feira", inicio: "08:50", fim: "13:50", local: "Cabine de Ciências Humanas" },
        { dia: "Sexta-feira", inicio: "08:50", fim: "13:00", local: "Cabine de Ciências Humanas" }
      ]
    },
    {
      nome: "Prof. Vitor Vasconcelos",
      disciplinas: ["Geografia"],
      horarios: [
        { dia: "Segunda-feira", inicio: "13:00", fim: "15:30", local: "Cabine de Ciências Humanas" },
        { dia: "Terça-feira", inicio: "18:00", fim: "20:30", local: "Cabine de Ciências Humanas" },
        { dia: "Quarta-feira", inicio: "11:20", fim: "15:30", local: "Cabine de Ciências Humanas" },
        { dia: "Quinta-feira", inicio: "13:00", fim: "20:30", local: "Cabine de Ciências Humanas" }
      ]
    },
    {
      nome: "Prof. David",
      disciplinas: ["Geografia"],
      horarios: [
        { dia: "Segunda-feira", inicio: "15:30", fim: "20:30", local: "Cabine de Ciências Humanas" },
        { dia: "Quarta-feira", inicio: "15:30", fim: "20:30", local: "Cabine de Ciências Humanas" }
      ]
    },
    {
      nome: "Prof. José Carlos",
      disciplinas: ["Geografia"],
      horarios: [
        { dia: "Sexta-feira", inicio: "08:50", fim: "17:10", local: "Cabine de Ciências Humanas" }
      ]
    },
    {
      nome: "Prof. Rafael Maia",
      disciplinas: ["Sociologia", "Filosofia"],
      horarios: [
        { dia: "Terça-feira", inicio: "13:00", fim: "20:30", local: "Cabine de Ciências Humanas" },
        { dia: "Quarta-feira", inicio: "13:00", fim: "18:00", local: "Cabine de Ciências Humanas" },
        { dia: "Sexta-feira", inicio: "13:00", fim: "17:10", local: "Cabine de Ciências Humanas" }
      ]
    },
    {
      nome: "Prof. Fernando",
      disciplinas: ["Sociologia", "Filosofia"],
      horarios: [
        { dia: "Quarta-feira", inicio: "08:50", fim: "13:00", local: "Cabine de Ciências Humanas" },
        { dia: "Quinta-feira", inicio: "08:50", fim: "11:20", local: "Cabine de Ciências Humanas" },
        { dia: "Quinta-feira", inicio: "18:00", fim: "20:30", local: "Cabine de Ciências Humanas" }
      ]
    }
  ],

  // ============================================================
  // DISCIPLINAS POR ÁREA
  // ============================================================
  disciplinas: [
    {
      area: "Linguagens e Códigos",
      cor: "#1565C0",
      icone: "💬",
      materias: [
        { nome: "Língua Portuguesa", fasciculos: 4 },
        { nome: "Língua Inglesa", fasciculos: 2 },
        { nome: "Língua Espanhola", fasciculos: 2 },
        { nome: "Artes", fasciculos: 1 },
        { nome: "Educação Física", fasciculos: 1 }
      ]
    },
    {
      area: "Ciências da Natureza",
      cor: "#2E7D32",
      icone: "🔬",
      materias: [
        { nome: "Biologia", fasciculos: 3 },
        { nome: "Química", fasciculos: 3 },
        { nome: "Física", fasciculos: 3 }
      ]
    },
    {
      area: "Ciências Humanas",
      cor: "#6A1B9A",
      icone: "🌍",
      materias: [
        { nome: "História", fasciculos: 3 },
        { nome: "Geografia", fasciculos: 3 },
        { nome: "Filosofia", fasciculos: 1 },
        { nome: "Sociologia", fasciculos: 1 }
      ]
    },
    {
      area: "Matemática",
      cor: "#E65100",
      icone: "📐",
      materias: [
        { nome: "Matemática", fasciculos: 4 }
      ]
    }
  ],

  // ============================================================
  // INFORMAÇÕES DE MATRÍCULA / REMATRÍCULA
  // ============================================================
  matricula: {
    periodo: "Matrícula aberta o ano todo",
    observacao: "Alunos com 18 ou mais podem se matricular para o ensino médio e com 15 ou mais para o ensino fundamental.",
    documentosNovos: [
      "RG (original)",
      "CPF (original)",
      "Comprovante de residência (original)",
      "Certidão de nascimento ou casamento (original)",
      "Histórico escolar (não aceitamos declaração)"
    ],
    horarioAtendimento: [
      { dia: "Segunda a Quinta", horario: "08:30 às 20:30" },
      { dia: "Sexta", horario: "08:30 às 17:10" },
      { dia: "Sábado", horario: "Fechado" }
    ],
    localAtendimento: "Secretaria — 2º Andar (Prédio do CIEP Nelson Ramos)",
    telefone: "(21) 98161-2512",
    observacoes: [
      "✅ Matrícula 100% gratuita",
      "✅ Não é necessário agendar horário",
      "⚠️ Documentos incompletos não serão aceitos",
      "📲 Dúvidas? Chame no WhatsApp!"
    ]
  }

};
