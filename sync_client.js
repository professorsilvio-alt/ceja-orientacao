/**
 * sync_client.js
 * Sincronização automática em tempo real dos horários a partir do Google Sheets.
 * 
 * Executa diretamente no navegador via JSONP (sem bloqueio de CORS).
 * Funciona tanto online quanto com fallback offline resiliente (localStorage / DADOS_ESCOLA).
 */

(function () {
  'use strict';

  const SPREADSHEET_ID = '1a2XewE5KNuadI8zUbi15r5n06roJb-wa';

  const ABAS = [
    { dia: 'Segunda-feira', gid: '765921185' },
    { dia: 'Terça-feira',   gid: '222847853' },
    { dia: 'Quarta-feira',  gid: '349244144' },
    { dia: 'Quinta-feira',  gid: '642475882' },
    { dia: 'Sexta-feira',   gid: '1997803226' },
  ];

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

  const NOMES_MAP = {
    'Leandro':            'Prof. Leandro',
    'Jordan':             'Prof. Jordan',
    'Arlindo':            'Prof. Arlindo',
    'Vitor':              'Prof. Vitor',
    'Sandra':             'Profª Sandra',
    'Luciana Cavalcante': 'Profª Luciana Cavalcante',
    'Luciana':            'Profª Luciana',
    'Daniela':            'Profª Daniela',
    'Rafael Souza':       'Prof. Rafael Souza',
    'Wanderley':          'Prof. Wanderley',
    'Thalles':            'Prof. Thalles',
    'Eliane':             'Profª Eliane',
    'Elaine':             'Profª Elaine',
    'Viviane':            'Profª Viviane',
    'Marcela':            'Profª Marcela',
    'Alessandra':         'Profª Alessandra',
    'Delma':              'Profª Delma',
    'Elázaro':            'Prof. Elázaro',
    'Elazaro':            'Prof. Elázaro',
    'Leonardo':           'Prof. Leonardo',
    'Xunei':              'Prof. Xunei',
    'Mário':              'Prof. Mário',
    'Mario':              'Prof. Mário',
    'Mário - Glp':        'Prof. Mário',
    'Mario - Glp':        'Prof. Mário',
    'Carlos Laurindo':    'Prof. Carlos Laurindo',
    'Fabiane':            'Profª Fabiane',
    'Vitor Vasconcelos':  'Prof. Vitor Vasconcelos',
    'David':              'Prof. David',
    'José Carlos':        'Prof. José Carlos',
    'Jose Carlos':        'Prof. José Carlos',
    'Rafael Maia':        'Prof. Rafael Maia',
    'Fernando':           'Prof. Fernando',
    'Rafael':             'Prof. Rafael',
  };

  const ORDEM_DIAS = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira'];

  function normalizeName(raw) {
    if (!raw) return '';
    let name = raw.replace(/[\s\-_]+(glp|\d+)$/i, '').trim();
    const words = name.split(/\s+/).map(w => {
      const low = w.toLowerCase();
      if (['de', 'da', 'do', 'dos', 'das', 'e'].includes(low)) return low;
      return w.charAt(0).toUpperCase() + w.slice(1).toLowerCase();
    });
    const cap = words.join(' ');
    return NOMES_MAP[cap] || (cap.startsWith('Prof') ? cap : `Prof. ${cap}`);
  }

  function fetchAbaJSONP(gid, timeoutMs = 8000) {
    return new Promise((resolve, reject) => {
      const callbackName = 'ceja_gviz_cb_' + gid + '_' + Math.floor(Math.random() * 1000000);
      const script = document.createElement('script');
      let timer = null;

      window[callbackName] = function (response) {
        cleanup();
        if (response && response.status === 'ok' && response.table) {
          resolve(response.table);
        } else {
          reject(new Error('Resposta inválida do Google Sheets'));
        }
      };

      function cleanup() {
        if (timer) clearTimeout(timer);
        delete window[callbackName];
        if (script.parentNode) script.parentNode.removeChild(script);
      }

      timer = setTimeout(() => {
        cleanup();
        reject(new Error(`Tempo esgotado ao buscar aba ${gid}`));
      }, timeoutMs);

      script.onerror = function () {
        cleanup();
        reject(new Error(`Falha de conexão com a aba ${gid}`));
      };

      script.src = `https://docs.google.com/spreadsheets/d/${SPREADSHEET_ID}/gviz/tq?tqx=responseHandler:${callbackName}&gid=${gid}&_t=${Date.now()}`;
      document.head.appendChild(script);
    });
  }

  function parseAbaTable(table, dia) {
    const rows = table.rows || [];
    let headerIdx = -1;

    for (let i = 0; i < rows.length; i++) {
      const r = rows[i];
      if (r && r.c && r.c[0]) {
        const val = String(r.c[0].v || '');
        if (/HOR[AÁ]RIOS/i.test(val)) {
          headerIdx = i;
          break;
        }
      }
    }

    if (headerIdx === -1) {
      console.warn(`[CEJA Sync] Cabeçalho 'HORÁRIOS' não encontrado na aba ${dia}`);
      return [];
    }

    const entradas = [];
    const timeRegex = /(\d{2}:\d{2})\s*[/–-]\s*(\d{2}:\d{2})/;

    for (let i = headerIdx + 1; i < rows.length; i++) {
      const r = rows[i];
      if (!r || !r.c || !r.c[0]) continue;
      const timeVal = String(r.c[0].v || '').trim();
      const match = timeVal.match(timeRegex);
      if (!match) continue;

      const inicio = match[1];
      const fim = match[2];

      for (let c = 1; c < 14; c++) {
        if (c >= r.c.length) continue;
        const cellObj = r.c[c];
        if (!cellObj || cellObj.v === null || cellObj.v === undefined) continue;

        let cellText = String(cellObj.v).trim().replace(/\n/g, ' / ');
        if (!cellText || cellText === 'FECHADA') continue;

        const nomesRaw = cellText.split('/');
        for (let j = 0; j < nomesRaw.length; j++) {
          const nomeTrim = nomesRaw[j].trim();
          if (nomeTrim && nomeTrim !== 'FECHADA') {
            entradas.append ? null : null;
            entradas.push({
              inicio: inicio,
              fim: fim,
              col: c - 1,
              nome: normalizeName(nomeTrim)
            });
          }
        }
      }
    }

    return entradas;
  }

  function buildHorarios(todosDados) {
    const mapa = {};

    todosDados.forEach(item => {
      item.entradas.forEach(e => {
        const col = e.col;
        if (col >= COLUNAS.length) return;
        const key = `${e.nome}___${item.dia}___${col}`;
        if (!mapa[key]) {
          mapa[key] = {
            nome: e.nome,
            dia: item.dia,
            disciplina: COLUNAS[col].disciplina,
            local: COLUNAS[col].local,
            slots: []
          };
        }
        mapa[key].slots.push({ inicio: e.inicio, fim: e.fim });
      });
    });

    const profMap = {};

    Object.keys(mapa).forEach(k => {
      const item = mapa[k];
      const nome = item.nome;
      if (!profMap[nome]) {
        profMap[nome] = {
          nome: nome,
          foto: '',
          disciplinas: new Set(),
          horarios: []
        };
      }

      const p = profMap[nome];
      p.disciplinas.add(item.disciplina);

      // Ordena slots e agrupa contíguos
      item.slots.sort((a, b) => a.inicio.localeCompare(b.inicio));
      const groups = [];
      if (item.slots.length > 0) {
        let currentGroup = [item.slots[0]];
        for (let i = 1; i < item.slots.length; i++) {
          const prev = currentGroup[currentGroup.length - 1];
          const curr = item.slots[i];
          if (curr.inicio === prev.fim) {
            currentGroup.push(curr);
          } else {
            groups.push(currentGroup);
            currentGroup = [curr];
          }
        }
        groups.push(currentGroup);
      }

      groups.forEach(g => {
        const entry = {
          dia: item.dia,
          inicio: g[0].inicio,
          fim: g[g.length - 1].fim,
          local: item.local
        };
        // Evita duplicatas exatas
        const exists = p.horarios.some(h => 
          h.dia === entry.dia && h.inicio === entry.inicio && h.fim === entry.fim && h.local === entry.local
        );
        if (!exists) {
          p.horarios.push(entry);
        }
      });
    });

    const result = [];
    const nomesSorted = Object.keys(profMap).sort((a, b) => a.localeCompare(b, 'pt-BR'));

    nomesSorted.forEach(nome => {
      const p = profMap[nome];
      p.horarios.sort((a, b) => {
        const idxA = ORDEM_DIAS.indexOf(a.dia);
        const idxB = ORDEM_DIAS.indexOf(b.dia);
        if (idxA !== idxB) return idxA - idxB;
        return a.inicio.localeCompare(b.inicio);
      });

      result.push({
        nome: p.nome,
        foto: '',
        disciplinas: Array.from(p.disciplinas).sort((a, b) => a.localeCompare(b, 'pt-BR')),
        horarios: p.horarios
      });
    });

    return result;
  }

  // Estado de sincronização
  let isSyncing = false;
  let lastSyncTime = null;
  let lastSyncSource = 'local'; // 'online' | 'cache' | 'local'

  // Recupera cache do localStorage na inicialização se existir
  try {
    const cached = localStorage.getItem('ceja_horarios_cache');
    if (cached) {
      const parsed = JSON.parse(cached);
      if (parsed && Array.isArray(parsed.data) && parsed.data.length > 0) {
        if (typeof DADOS_ESCOLA !== 'undefined') {
          DADOS_ESCOLA.horarioProfessores = parsed.data;
          lastSyncSource = 'cache';
          lastSyncTime = new Date(parsed.timestamp || Date.now());
          console.log(`[CEJA Sync] Horários carregados do cache local (${parsed.data.length} professores).`);
        }
      }
    }
  } catch (e) {
    console.warn('[CEJA Sync] Não foi possível ler o cache local:', e);
  }

  async function syncHorariosOnline(options = {}) {
    const force = options.force || false;

    // Evita múltiplas chamadas simultâneas
    if (isSyncing) {
      console.log('[CEJA Sync] Sincronização já em andamento.');
      return { success: false, inProgress: true };
    }

    // Se já sincronizou há menos de 3 minutos e não foi forçado, reaproveita
    const THREE_MINUTES = 3 * 60 * 1000;
    if (!force && lastSyncSource === 'online' && lastSyncTime && (Date.now() - lastSyncTime.getTime()) < THREE_MINUTES) {
      console.log('[CEJA Sync] Dados online recentes, reutilizando.');
      return { success: true, cached: true, source: 'online', timestamp: lastSyncTime };
    }

    isSyncing = true;
    notifyStatusChange('syncing', 'Consultando planilha online...');

    try {
      // Busca as 5 abas em paralelo
      const promises = ABAS.map(aba => 
        fetchAbaJSONP(aba.gid, 8000)
          .then(table => ({
            dia: aba.dia,
            entradas: parseAbaTable(table, aba.dia)
          }))
      );

      const todosDados = await Promise.all(promises);
      const novoHorario = buildHorarios(todosDados);

      if (!novoHorario || novoHorario.length === 0) {
        throw new Error('Nenhum horário retornado da planilha.');
      }

      // Atualiza o objeto global
      if (typeof DADOS_ESCOLA !== 'undefined') {
        DADOS_ESCOLA.horarioProfessores = novoHorario;
      }

      lastSyncTime = new Date();
      lastSyncSource = 'online';

      // Salva no localStorage para uso offline posterior
      try {
        localStorage.setItem('ceja_horarios_cache', JSON.stringify({
          timestamp: lastSyncTime.getTime(),
          data: novoHorario
        }));
      } catch (e) {
        console.warn('[CEJA Sync] Falha ao gravar no localStorage:', e);
      }

      isSyncing = false;
      notifyStatusChange('online', `Atualizado da planilha online (${formatTime(lastSyncTime)})`);

      // Dispara evento customizado para a UI atualizar
      window.dispatchEvent(new CustomEvent('ceja-horarios-updated', {
        detail: {
          success: true,
          source: 'online',
          timestamp: lastSyncTime,
          count: novoHorario.length
        }
      }));

      return { success: true, count: novoHorario.length, timestamp: lastSyncTime };

    } catch (err) {
      console.warn('[CEJA Sync] Falha na consulta online:', err.message);
      isSyncing = false;

      // Fallback offline
      const msgOffline = lastSyncSource === 'cache' 
        ? `Modo offline (usando cache de ${formatTime(lastSyncTime)})`
        : 'Modo offline (exibindo horário salvo)';

      notifyStatusChange('offline', msgOffline);

      window.dispatchEvent(new CustomEvent('ceja-horarios-updated', {
        detail: {
          success: false,
          error: err.message,
          source: lastSyncSource,
          timestamp: lastSyncTime
        }
      }));

      return { success: false, error: err.message, fallbackSource: lastSyncSource };
    }
  }

  function formatTime(date) {
    if (!date) return '';
    const h = String(date.getHours()).padStart(2, '0');
    const m = String(date.getMinutes()).padStart(2, '0');
    return `${h}:${m}`;
  }

  function notifyStatusChange(state, text) {
    const elText = document.getElementById('sync-status-text');
    const elDot = document.querySelector('.sync-status-badge .status-dot');
    const btnSync = document.getElementById('btn-sync-horarios');

    if (elText) elText.textContent = text;

    if (elDot) {
      elDot.className = 'status-dot ' + state;
    }

    if (btnSync) {
      if (state === 'syncing') {
        btnSync.classList.add('loading');
      } else {
        btnSync.classList.remove('loading');
      }
    }
  }

  // Expõe API global
  window.CEJA_SYNC = {
    syncHorariosOnline: syncHorariosOnline,
    getStatus: () => ({ isSyncing, lastSyncTime, lastSyncSource })
  };

})();
