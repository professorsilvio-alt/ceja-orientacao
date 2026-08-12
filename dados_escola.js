/**
 * dados_escola.js
 * Arquivo de configuracao do CEJA Professora Rosa Soares
 * Edite este arquivo para atualizar os dados exibidos no totem.
 */

const DADOS_ESCOLA = {

  // ============================================================
  // HORARIO DOS PROFESSORES
  // ============================================================
  // HORARIOS_SYNC_START
  horarioProfessores: [
    {
      nome: "Prof. Arlindo",
      foto: "",
      disciplinas: ["MatemÃ¡tica"],
      horarios: [
        { dia: "Quarta-feira", inicio: "08:50", fim: "17:10", local: "Cabine de MatemÃ¡tica" },
        { dia: "Quinta-feira", inicio: "08:50", fim: "20:30", local: "Cabine de MatemÃ¡tica" }
      ]
    },
    {
      nome: "Prof. Carlos Laurindo",
      foto: "",
      disciplinas: ["HistÃ³ria"],
      horarios: [
        { dia: "TerÃ§a-feira", inicio: "12:10", fim: "17:10", local: "Cabine de CiÃªncias Humanas" },
        { dia: "Quinta-feira", inicio: "12:10", fim: "17:10", local: "Cabine de CiÃªncias Humanas" }
      ]
    },
    {
      nome: "Prof. David",
      foto: "",
      disciplinas: ["Geografia"],
      horarios: [
        { dia: "Segunda-feira", inicio: "15:30", fim: "20:30", local: "Cabine de CiÃªncias Humanas" },
        { dia: "Quarta-feira", inicio: "15:30", fim: "20:30", local: "Cabine de CiÃªncias Humanas" }
      ]
    },
    {
      nome: "Prof. Elazaro",
      foto: "",
      disciplinas: ["CiÃªncias/Biologia"],
      horarios: [
        { dia: "Quinta-feira", inicio: "08:50", fim: "12:10", local: "Cabine de CiÃªncias da Natureza" },
        { dia: "Sexta-feira", inicio: "08:50", fim: "15:30", local: "Cabine de CiÃªncias da Natureza" }
      ]
    },
    {
      nome: "Prof. Fernando",
      foto: "",
      disciplinas: ["Filosofia", "Sociologia"],
      horarios: [
        { dia: "Quarta-feira", inicio: "08:50", fim: "13:00", local: "Cabine de CiÃªncias Humanas" },
        { dia: "Quinta-feira", inicio: "08:50", fim: "13:50", local: "Cabine de CiÃªncias Humanas" }
      ]
    },
    {
      nome: "Prof. Jordan",
      foto: "",
      disciplinas: ["MatemÃ¡tica"],
      horarios: [
        { dia: "Segunda-feira", inicio: "16:20", fim: "20:30", local: "Cabine de MatemÃ¡tica" },
        { dia: "TerÃ§a-feira", inicio: "13:00", fim: "20:30", local: "Cabine de MatemÃ¡tica" },
        { dia: "Quarta-feira", inicio: "17:10", fim: "20:30", local: "Cabine de MatemÃ¡tica" },
        { dia: "Quinta-feira", inicio: "16:20", fim: "18:00", local: "Cabine de MatemÃ¡tica" }
      ]
    },
    {
      nome: "Prof. Jose Carlos",
      foto: "",
      disciplinas: ["Geografia"],
      horarios: [
        { dia: "Sexta-feira", inicio: "08:50", fim: "17:10", local: "Cabine de CiÃªncias Humanas" }
      ]
    },
    {
      nome: "Prof. Leandro",
      foto: "",
      disciplinas: ["MatemÃ¡tica"],
      horarios: [
        { dia: "Segunda-feira", inicio: "08:50", fim: "18:00", local: "Cabine de MatemÃ¡tica" },
        { dia: "TerÃ§a-feira", inicio: "08:50", fim: "13:00", local: "Cabine de MatemÃ¡tica" },
        { dia: "Quarta-feira", inicio: "14:40", fim: "18:00", local: "Cabine de MatemÃ¡tica" }
      ]
    },
    {
      nome: "Prof. Leonardo",
      foto: "",
      disciplinas: ["FÃ­sica"],
      horarios: [
        { dia: "TerÃ§a-feira", inicio: "08:50", fim: "14:40", local: "Cabine de CiÃªncias da Natureza" },
        { dia: "Quarta-feira", inicio: "08:50", fim: "14:40", local: "Cabine de CiÃªncias da Natureza" },
        { dia: "Quinta-feira", inicio: "08:50", fim: "13:50", local: "Cabine de CiÃªncias da Natureza" }
      ]
    },
    {
      nome: "Prof. Mario",
      foto: "",
      disciplinas: ["HistÃ³ria"],
      horarios: [
        { dia: "Segunda-feira", inicio: "13:50", fim: "20:30", local: "Cabine de CiÃªncias Humanas" },
        { dia: "Sexta-feira", inicio: "13:50", fim: "17:10", local: "Cabine de CiÃªncias Humanas" }
      ]
    },
    {
      nome: "Prof. Rafael Maia",
      foto: "",
      disciplinas: ["Filosofia", "Sociologia"],
      horarios: [
        { dia: "Segunda-feira", inicio: "13:00", fim: "13:50", local: "Cabine de CiÃªncias Humanas" },
        { dia: "Segunda-feira", inicio: "13:50", fim: "15:30", local: "Cabine de CiÃªncias Humanas" },
        { dia: "TerÃ§a-feira", inicio: "13:00", fim: "20:30", local: "Cabine de CiÃªncias Humanas" },
        { dia: "Quarta-feira", inicio: "13:00", fim: "16:20", local: "Cabine de CiÃªncias Humanas" },
        { dia: "Sexta-feira", inicio: "13:00", fim: "15:30", local: "Cabine de CiÃªncias Humanas" },
        { dia: "Sexta-feira", inicio: "15:30", fim: "16:20", local: "Cabine de CiÃªncias Humanas" }
      ]
    },
    {
      nome: "Prof. Rafael Souza",
      foto: "",
      disciplinas: ["Espanhol"],
      horarios: [
        { dia: "Segunda-feira", inicio: "13:50", fim: "19:40", local: "Cabine de Linguagens" },
        { dia: "TerÃ§a-feira", inicio: "08:50", fim: "13:00", local: "Cabine de Linguagens" }
      ]
    },
    {
      nome: "Prof. Thalles",
      foto: "",
      disciplinas: ["EducaÃ§Ã£o ArtÃ­stica"],
      horarios: [
        { dia: "TerÃ§a-feira", inicio: "14:40", fim: "20:30", local: "Cabine de Linguagens" },
        { dia: "Quinta-feira", inicio: "08:50", fim: "13:00", local: "Cabine de Linguagens" }
      ]
    },
    {
      nome: "Prof. Vitor",
      foto: "",
      disciplinas: ["MatemÃ¡tica"],
      horarios: [
        { dia: "TerÃ§a-feira", inicio: "18:00", fim: "18:50", local: "Cabine de MatemÃ¡tica" },
        { dia: "Sexta-feira", inicio: "08:50", fim: "17:10", local: "Cabine de MatemÃ¡tica" }
      ]
    },
    {
      nome: "Prof. Vitor Vasconcelos",
      foto: "",
      disciplinas: ["Geografia"],
      horarios: [
        { dia: "Segunda-feira", inicio: "13:00", fim: "15:30", local: "Cabine de CiÃªncias Humanas" },
        { dia: "TerÃ§a-feira", inicio: "13:50", fim: "20:30", local: "Cabine de CiÃªncias Humanas" },
        { dia: "Quinta-feira", inicio: "13:00", fim: "20:30", local: "Cabine de CiÃªncias Humanas" }
      ]
    },
    {
      nome: "Prof. Wanderley",
      foto: "",
      disciplinas: ["InglÃªs"],
      horarios: [
        { dia: "Quarta-feira", inicio: "10:30", fim: "16:20", local: "Cabine de Linguagens" },
        { dia: "Sexta-feira", inicio: "12:10", fim: "16:20", local: "Cabine de Linguagens" }
      ]
    },
    {
      nome: "Prof. Xunei",
      foto: "",
      disciplinas: ["FÃ­sica"],
      horarios: [
        { dia: "TerÃ§a-feira", inicio: "14:40", fim: "19:40", local: "Cabine de CiÃªncias da Natureza" },
        { dia: "Quarta-feira", inicio: "15:30", fim: "20:30", local: "Cabine de CiÃªncias da Natureza" }
      ]
    },
    {
      nome: "Prof.Âª Alessandra",
      foto: "",
      disciplinas: ["CiÃªncias/Biologia", "QuÃ­mica"],
      horarios: [
        { dia: "Segunda-feira", inicio: "12:10", fim: "16:20", local: "Cabine de CiÃªncias da Natureza" },
        { dia: "Segunda-feira", inicio: "16:20", fim: "20:30", local: "Cabine de CiÃªncias da Natureza" },
        { dia: "TerÃ§a-feira", inicio: "08:50", fim: "13:00", local: "Cabine de CiÃªncias da Natureza" },
        { dia: "Quinta-feira", inicio: "13:00", fim: "17:10", local: "Cabine de CiÃªncias da Natureza" }
      ]
    },
    {
      nome: "Prof.Âª Daniela",
      foto: "",
      disciplinas: ["PortuguÃªs"],
      horarios: [
        { dia: "Quarta-feira", inicio: "13:50", fim: "18:50", local: "Cabine de Linguagens" },
        { dia: "Quinta-feira", inicio: "13:50", fim: "20:30", local: "Cabine de Linguagens" },
        { dia: "Sexta-feira", inicio: "08:50", fim: "17:10", local: "Cabine de Linguagens" }
      ]
    },
    {
      nome: "Prof.Âª Delma",
      foto: "",
      disciplinas: ["CiÃªncias/Biologia"],
      horarios: [
        { dia: "Segunda-feira", inicio: "08:50", fim: "12:10", local: "Cabine de CiÃªncias da Natureza" },
        { dia: "TerÃ§a-feira", inicio: "15:30", fim: "20:30", local: "Cabine de CiÃªncias da Natureza" },
        { dia: "Quarta-feira", inicio: "15:30", fim: "20:30", local: "Cabine de CiÃªncias da Natureza" }
      ]
    },
    {
      nome: "Prof.Âª Elaine",
      foto: "",
      disciplinas: ["PortuguÃªs"],
      horarios: [
        { dia: "Segunda-feira", inicio: "13:50", fim: "20:30", local: "Cabine de Linguagens" }
      ]
    },
    {
      nome: "Prof.Âª Eliane",
      foto: "",
      disciplinas: ["EducaÃ§Ã£o FÃ­sica"],
      horarios: [
        { dia: "TerÃ§a-feira", inicio: "15:30", fim: "20:30", local: "Cabine de Linguagens" },
        { dia: "Quinta-feira", inicio: "11:20", fim: "16:20", local: "Cabine de Linguagens" }
      ]
    },
    {
      nome: "Prof.Âª Fabiane",
      foto: "",
      disciplinas: ["HistÃ³ria"],
      horarios: [
        { dia: "Quarta-feira", inicio: "08:50", fim: "13:50", local: "Cabine de CiÃªncias Humanas" },
        { dia: "Sexta-feira", inicio: "08:50", fim: "13:00", local: "Cabine de CiÃªncias Humanas" }
      ]
    },
    {
      nome: "Prof.Âª Luciana",
      foto: "",
      disciplinas: ["PortuguÃªs", "InglÃªs"],
      horarios: [
        { dia: "Segunda-feira", inicio: "14:40", fim: "20:30", local: "Cabine de Linguagens" },
        { dia: "Quinta-feira", inicio: "14:40", fim: "18:50", local: "Cabine de Linguagens" },
        { dia: "Quinta-feira", inicio: "18:50", fim: "20:30", local: "Cabine de Linguagens" }
      ]
    },
    {
      nome: "Prof.Âª Luciana Cavalcante",
      foto: "",
      disciplinas: ["PortuguÃªs"],
      horarios: [
        { dia: "TerÃ§a-feira", inicio: "12:10", fim: "20:30", local: "Cabine de Linguagens" }
      ]
    },
    {
      nome: "Prof.Âª Marcela",
      foto: "",
      disciplinas: ["QuÃ­mica"],
      horarios: [
        { dia: "Quarta-feira", inicio: "08:50", fim: "13:50", local: "Cabine de CiÃªncias da Natureza" }
      ]
    },
    {
      nome: "Prof.Âª Sandra",
      foto: "",
      disciplinas: ["PortuguÃªs"],
      horarios: [
        { dia: "Segunda-feira", inicio: "08:50", fim: "13:00", local: "Cabine de Linguagens" },
        { dia: "TerÃ§a-feira", inicio: "08:50", fim: "12:10", local: "Cabine de Linguagens" },
        { dia: "Quarta-feira", inicio: "09:40", fim: "13:50", local: "Cabine de Linguagens" },
        { dia: "Quinta-feira", inicio: "08:50", fim: "13:50", local: "Cabine de Linguagens" }
      ]
    },
    {
      nome: "Prof.Âª Viviane",
      foto: "",
      disciplinas: ["QuÃ­mica"],
      horarios: [
        { dia: "Segunda-feira", inicio: "08:50", fim: "13:50", local: "Cabine de CiÃªncias da Natureza" },
        { dia: "TerÃ§a-feira", inicio: "08:50", fim: "13:50", local: "Cabine de CiÃªncias da Natureza" },
        { dia: "Quinta-feira", inicio: "08:50", fim: "12:10", local: "Cabine de CiÃªncias da Natureza" },
        { dia: "Sexta-feira", inicio: "08:50", fim: "12:10", local: "Cabine de CiÃªncias da Natureza" }
      ]
    }
  ],
  // HORARIOS_SYNC_END

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
  // INFORMACOES DE MATRICULA / REMATRICULA
  // ============================================================
  matricula: {
    periodo: "Matrícula aberta o ano todo",
    observacao: "Alunos com 18 anos ou mais podem se matricular para o ensino médio e com 15 anos ou mais para o ensino fundamental.",
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
    localAtendimento: "Secretaria - 2º Andar (Prédio do CIEP Nelson Ramos)",
    telefone: "(21) 98161-2512",
    observacoes: [
      "Matrícula 100% gratuita",
      "Não é necessário agendar horário",
      "Documentos incompletos não serão aceitos",
      "Dúvidas? Chame no WhatsApp!"
    ]
  }

};
