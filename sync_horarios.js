/**
 * sync_horarios.js
 * Sincroniza os horários dos professores a partir da planilha Google Sheets.
 *
 * COMO USAR:
 *   node sync_horarios.js
 *
 * Execute este script manualmente ou configure uma tarefa agendada no Windows
 * para rodar automaticamente uma vez por dia.
 *
 * O script lê as 5 abas "SEGUNDA ALUNO" a "SEXTA ALUNO" da planilha,
 * converte os dados e regera o bloco horarioProfessores em dados_escola.js.
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

// ── CONFIGURAÇÃO ──────────────────────────────────────────────────────────────

const SPREADSHEET_ID = '1a2XewE5KNuadI8zUbi15r5n06roJb-wa';

// GIDs das abas (obtidos da planilha)
const ABAS = [
  { dia: 'Segunda-feira', gid: '765921185' },
  { dia: 'Terça-feira',   gid: '222847853' },
  { dia: 'Quarta-feira',  gid: '349244144' },
  { dia: 'Quinta-feira',  gid: '642475882' },
  { dia: 'Sexta-feira',   gid: '1997803226' },
];

// Mapeamento: coluna CSV → disciplina e local (cabine)
const COLUNAS = [
  { disciplina: 'Matemática',         local: 'Cabine de Matemática' },
  { disciplina: 'Português',          local: 'Cabine de Linguagens' },
  { disciplina: 'Inglês',             local: 'Cabine de Linguagens' },
  { disciplina: 'Espanhol',           local: 'Cabine de Linguagens' },
  { disciplina: 'Educação Artística', local: 'Cabine de Linguagens' },
  { disciplina: 'Educação Física',    local: 'Cabine de Linguagens' },
  { disciplina: 'Ciências/Biologia',  local: 'Cabine de Ciências da Natureza' },
  { disciplina: 'Física',             local: 'Cabine de Ciências da Natureza' },
  { disciplina: 'Química',            local: 'Cabine de Ciências da Natureza' },
  { disciplina: 'História',           local: 'Cabine de Ciências Humanas' },
  { disciplina: 'Geografia',          local: 'Cabine de Ciências Humanas' },
  { disciplina: 'Sociologia',         local: 'Cabine de Ciências Humanas' },
  { disciplina: 'Filosofia',          local: 'Cabine de Ciências Humanas' },
];

// Caminho do arquivo de destino
const DADOS_ESCOLA_PATH = path.join(__dirname, 'dados_escola.js');

// ── FUNÇÕES AUXILIARES ────────────────────────────────────────────────────────

/**
 * Busca o CSV de uma aba da planilha via HTTPS.
 */
function fetchCSV(gid) {
  return new Promise((resolve, reject) => {
    const url = `https://docs.google.com/spreadsheets/d/${SPREADSHEET_ID}/export?format=csv&gid=${gid}`;
    const request = (reqUrl) => {
      https.get(reqUrl, (res) => {
        if (res.statusCode === 302 || res.statusCode === 301) {
          request(res.headers.location);
          return;
        }
        let data = '';
        res.on('data', chunk => { data += chunk; });
        res.on('end', () => resolve(data));
        res.on('error', reject);
      }).on('error', reject);
    };
    request(url);
  });
}

/**
 * Parseia uma linha CSV respeitando campos entre aspas com quebras de linha.
 */
function parseCSVLine(line) {
  const result = [];
  let current = '';
  let inQuotes = false;

  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (ch === '"') {
      if (inQuotes && line[i + 1] === '"') {
        current += '"';
        i++;
      } else {
        inQuotes = !inQuotes;
      }
    } else if (ch === ',' && !inQuotes) {
      result.push(current);
      current = '';
    } else {
      current += ch;
    }
  }
  result.push(current);
  return result;
}

/**
 * Analisa o CSV de uma aba e retorna as entradas de horário.
 */
function parseCSV(csvText, dia) {
  // Normaliza: junta linhas dentro de campos com aspas antes de dividir
  // Estratégia: dividir pelo padrão de linha de horário
  const linhas = csvText.replace(/\r\n/g, '\n').replace(/\r/g, '\n').split('\n');

  // Reagrupa linhas quebradas por campos com aspas
  const linhasReagrupadas = [];
  let buffer = '';
  let emAspas = 0;
  for (const linha of linhas) {
    for (const ch of linha) {
      if (ch === '"') emAspas = emAspas === 0 ? 1 : 0;
    }
    buffer += (buffer ? '\n' : '') + linha;
    if (emAspas === 0) {
      linhasReagrupadas.push(buffer);
      buffer = '';
    }
  }
  if (buffer) linhasReagrupadas.push(buffer);

  // Encontra linha de cabeçalho (HORÁRIOS)
  let headerIdx = -1;
  for (let i = 0; i < linhasReagrupadas.length; i++) {
    if (linhasReagrupadas[i].match(/^"?HORÁRIOS/)) {
      headerIdx = i;
      break;
    }
  }
  if (headerIdx === -1) {
    console.warn(`  [${dia}] Linha HORÁRIOS não encontrada.`);
    return [];
  }

  const entradas = [];

  for (let i = headerIdx + 1; i < linhasReagrupadas.length; i++) {
    const linha = linhasReagrupadas[i].trim();
    if (!linha) continue;

    const cols = parseCSVLine(linha);
    if (cols.length < 2) continue;

    const horarioCell = cols[0].replace(/"/g, '').trim();

    // Linha de horário: "08:50/ 09:40"
    const match = horarioCell.match(/(\d{2}:\d{2})\s*[\/]\s*(\d{2}:\d{2})/);
    if (!match) continue;

    const inicio = match[1];
    const fim = match[2];

    // Verifica se toda a linha é FECHADA
    const todosValores = cols.slice(1).map(c => c.replace(/"/g, '').trim());
    if (todosValores.every(v => v === 'FECHADA' || v === '')) continue;

    for (let c = 1; c <= 13 && c < cols.length; c++) {
      const cell = cols[c].replace(/"/g, '').replace(/\n/g, ' / ').trim();
      if (!cell || cell === 'FECHADA') continue;

      // Pode haver múltiplos professores separados por "/"
      const nomes = cell.split('/').map(n => n.trim()).filter(n => n && n !== 'FECHADA');
      for (const nome of nomes) {
        entradas.push({
          horarioInicio: inicio,
          horarioFim: fim,
          colIndex: c - 1,
          nomeProfessor: normalizarNome(nome),
        });
      }
    }
  }

  return entradas;
}

/**
 * Normaliza o nome do professor para formato de título.
 */
function normalizarNome(nomeRaw) {
  // Sufixos numéricos como "LUCIANA 1", "ARLINDO 2" → remove o número
  const semSufixo = nomeRaw.replace(/\s+\d+$/, '').trim();

  return semSufixo
    .toLowerCase()
    .split(/\s+/)
    .map(w => {
      if (!w) return '';
      if (['de', 'da', 'do', 'dos', 'das', 'e'].includes(w)) return w;
      return w.charAt(0).toUpperCase() + w.slice(1);
    })
    .join(' ');
}

/**
 * Converte as entradas de horário para o formato horarioProfessores.
 * Agrupa por professor + dia, consolidando o horário de início e fim do dia.
 */
function construirHorarioProfessores(todosDados) {
  // Mapa: "nomeProfessor|dia|colIndex" → { slots: [{inicio, fim}], local }
  const mapa = new Map();

  for (const { dia, entradas } of todosDados) {
    for (const entrada of entradas) {
      const col = COLUNAS[entrada.colIndex];
      if (!col) continue;

      const chave = `${entrada.nomeProfessor}|||${dia}|||${entrada.colIndex}`;

      if (!mapa.has(chave)) {
        mapa.set(chave, {
          nome: entrada.nomeProfessor,
          dia,
          local: col.local,
          disciplina: col.disciplina,
          slots: [],
        });
      }
      mapa.get(chave).slots.push({ inicio: entrada.horarioInicio, fim: entrada.horarioFim });
    }
  }

  // Agrupa por professor
  const professorMap = new Map();

  for (const [, item] of mapa.entries()) {
    if (!professorMap.has(item.nome)) {
      professorMap.set(item.nome, { nome: item.nome, foto: '', disciplinas: new Set(), horarios: [] });
    }

    const prof = professorMap.get(item.nome);
    prof.disciplinas.add(item.disciplina);

    // Consolida slots: agrupa apenas slots contíguos (onde o início do próximo é igual ao fim do anterior)
    const sorted = item.slots.sort((a, b) => a.inicio.localeCompare(b.inicio));
    const groups = [];
    if (sorted.length > 0) {
      let currentGroup = [sorted[0]];
      for (let i = 1; i < sorted.length; i++) {
        const prev = currentGroup[currentGroup.length - 1];
        const curr = sorted[i];
        if (curr.inicio === prev.fim) {
          currentGroup.push(curr);
        } else {
          groups.push(currentGroup);
          currentGroup = [curr];
        }
      }
      groups.push(currentGroup);
    }

    for (const group of groups) {
      const inicio = group[0].inicio;
      const fim = group[group.length - 1].fim;
      
      // Evita duplicatas exatas
      const jaExiste = prof.horarios.some(
        h => h.dia === item.dia && h.inicio === inicio && h.fim === fim && h.local === item.local
      );
      if (!jaExiste) {
        prof.horarios.push({ dia: item.dia, inicio, fim, local: item.local });
      }
    }
  }

  const ORDEM_DIAS = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira'];

  const resultado = [];
  for (const [, prof] of professorMap.entries()) {
    prof.horarios.sort((a, b) =>
      ORDEM_DIAS.indexOf(a.dia) - ORDEM_DIAS.indexOf(b.dia) || a.inicio.localeCompare(b.inicio)
    );
    resultado.push({
      nome: prof.nome,
      foto: prof.foto,
      disciplinas: [...prof.disciplinas],
      horarios: prof.horarios,
    });
  }

  return resultado.sort((a, b) => a.nome.localeCompare(b.nome, 'pt-BR'));
}

/**
 * Gera o texto JavaScript do bloco horarioProfessores.
 */
function gerarBlocoJS(horarios) {
  const linhas = ['['];
  for (let i = 0; i < horarios.length; i++) {
    const p = horarios[i];
    const virgula = i < horarios.length - 1 ? ',' : '';
    linhas.push('    {');
    linhas.push(`      nome: ${JSON.stringify(p.nome)},`);
    linhas.push(`      foto: "",`);
    linhas.push(`      disciplinas: ${JSON.stringify(p.disciplinas)},`);
    linhas.push('      horarios: [');
    for (let j = 0; j < p.horarios.length; j++) {
      const h = p.horarios[j];
      const vH = j < p.horarios.length - 1 ? ',' : '';
      linhas.push(`        { dia: ${JSON.stringify(h.dia)}, inicio: "${h.inicio}", fim: "${h.fim}", local: ${JSON.stringify(h.local)} }${vH}`);
    }
    linhas.push('      ]');
    linhas.push(`    }${virgula}`);
  }
  linhas.push('  ]');
  return linhas.join('\n');
}

/**
 * Substitui o bloco horarioProfessores no dados_escola.js.
 */
function atualizarDadosEscola(conteudoAtual, novoHorario) {
  const novoBloco = gerarBlocoJS(novoHorario);
  const startMarker = '// HORARIOS_SYNC_START';
  const endMarker = '// HORARIOS_SYNC_END';

  const startIndex = conteudoAtual.indexOf(startMarker);
  const endIndex = conteudoAtual.indexOf(endMarker);

  if (startIndex === -1 || endIndex === -1) {
    throw new Error('Marcadores HORARIOS_SYNC não encontrados em dados_escola.js');
  }

  const part1 = conteudoAtual.substring(0, startIndex + startMarker.length);
  const part2 = conteudoAtual.substring(endIndex);

  return part1 + '\n  horarioProfessores: ' + novoBloco + ',\n  ' + part2;
}

/**
 * Hash simples para comparar mudanças.
 */
function hashSimples(obj) {
  const str = JSON.stringify(obj);
  let hash = 5381;
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) + hash + str.charCodeAt(i)) >>> 0;
  }
  return hash.toString(16);
}

// ── EXECUÇÃO PRINCIPAL ────────────────────────────────────────────────────────

async function main() {
  const agora = new Date().toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo' });
  console.log('\n========================================');
  console.log(' CEJA - Sincronizador de Horários');
  console.log(` ${agora}`);
  console.log('========================================\n');

  // 1. Busca todos os CSVs
  console.log('1️⃣  Buscando dados da planilha...\n');
  const todosDados = [];

  for (const aba of ABAS) {
    process.stdout.write(`   📥 ${aba.dia}... `);
    try {
      const csv = await fetchCSV(aba.gid);
      const entradas = parseCSV(csv, aba.dia);
      todosDados.push({ dia: aba.dia, entradas });
      console.log(`✅ (${entradas.length} entradas)`);
    } catch (err) {
      console.log(`❌ Erro: ${err.message}`);
      process.exit(1);
    }
  }

  // 2. Constrói a estrutura
  console.log('\n2️⃣  Consolidando horários...');
  const novoHorario = construirHorarioProfessores(todosDados);
  console.log(`   ${novoHorario.length} professores encontrados.\n`);

  // 3. Lê arquivo atual
  console.log('3️⃣  Verificando dados_escola.js...');
  if (!fs.existsSync(DADOS_ESCOLA_PATH)) {
    console.error(`   ❌ Arquivo não encontrado: ${DADOS_ESCOLA_PATH}`);
    process.exit(1);
  }
  const conteudoAtual = fs.readFileSync(DADOS_ESCOLA_PATH, 'utf-8');

  // Extrai horário atual (exec com eval para comparação)
  let hashAtual = '';
  const startMarker = '// HORARIOS_SYNC_START';
  const endMarker = '// HORARIOS_SYNC_END';
  const startIndex = conteudoAtual.indexOf(startMarker);
  const endIndex = conteudoAtual.indexOf(endMarker);
  
  if (startIndex !== -1 && endIndex !== -1) {
    const blocoAtualStr = conteudoAtual.substring(startIndex + startMarker.length, endIndex);
    const matchArray = blocoAtualStr.match(/horarioProfessores:\s*(\[[\s\S]*\])/);
    if (matchArray) {
      try {
        // eslint-disable-next-line no-eval
        hashAtual = hashSimples(eval(matchArray[1]));
      } catch (_) { /* ignora */ }
    }
  }

  const hashNovo = hashSimples(novoHorario);

  if (hashAtual === hashNovo) {
    console.log('   ✅ Sem alterações — dados_escola.js já está atualizado.\n');
    return;
  }

  // 4. Atualiza
  console.log('   ⚠️  Alterações detectadas! Atualizando...');
  const novoConteudo = atualizarDadosEscola(conteudoAtual, novoHorario);
  fs.writeFileSync(DADOS_ESCOLA_PATH, novoConteudo, 'utf-8');
  console.log('   ✅ dados_escola.js atualizado!\n');

  // 5. Resumo
  console.log('4️⃣  Professores sincronizados:');
  for (const prof of novoHorario) {
    console.log(`   • ${prof.nome} | ${prof.disciplinas.join(', ')} | ${prof.horarios.length} dia(s)`);
  }

  console.log('\n========================================\n');
}

main().catch(err => {
  console.error('\n❌ Erro fatal:', err.message);
  console.error(err.stack);
  process.exit(1);
});
