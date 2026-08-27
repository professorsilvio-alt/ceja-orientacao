/**
 * script.js v2.0 — CEJA Autoatendimento Totem
 */
document.addEventListener('DOMContentLoaded', () => {

  // ==========================================================================
  // 1. RELÓGIO EM TEMPO REAL
  // ==========================================================================
  const kioskTime = document.getElementById('kiosk-time');
  const kioskDate = document.getElementById('kiosk-date');

  function updateClock() {
    const now = new Date();
    const h = String(now.getHours()).padStart(2, '0');
    const m = String(now.getMinutes()).padStart(2, '0');
    const s = String(now.getSeconds()).padStart(2, '0');
    kioskTime.textContent = `${h}:${m}:${s}`;

    const opts = { weekday: 'long', day: '2-digit', month: 'long', year: 'numeric' };
    kioskDate.textContent = now.toLocaleDateString('pt-BR', opts);
  }

  updateClock();
  setInterval(updateClock, 1000);


  // ==========================================================================
  // 2. NAVEGAÇÃO SPA — SISTEMA DE TELAS
  // ==========================================================================
  const allScreens    = document.querySelectorAll('.screen');
  const backBtn       = document.getElementById('kiosk-back-btn');
  const breadcrumb    = document.getElementById('kiosk-breadcrumb');
  const logoBtn       = document.getElementById('kiosk-logo-btn');

  const screenLabels = {
    'screen-home':         '🏠 Início',
    'screen-avaliacoes':   '📋 Avaliações',
    'screen-simulador':    '🎯 Simulador de Notas',
    'screen-horarios':     '🗓️ Horário Semanal da Escola',
    'screen-matricula':    '📝 Matrícula',
    'screen-disciplinas':  '📚 Disciplinas',
    'screen-faleconosco':  '💬 Fale Conosco',
  };

  let currentScreen = 'screen-home';
  const renderedScreens = new Set(); // track which dynamic screens have been rendered

  function showScreen(targetId) {
    if (targetId === currentScreen) return;

    const current = document.getElementById(currentScreen);
    const target  = document.getElementById(targetId);
    if (!target) return;

    // Lazy-render dynamic screens on first visit
    if (!renderedScreens.has(targetId)) {
      if (targetId === 'screen-horarios')    renderHorarios();
      if (targetId === 'screen-matricula')   renderMatricula();
      if (targetId === 'screen-disciplinas') renderDisciplinas();
      renderedScreens.add(targetId);
    }

    // Exit current
    if (current) {
      current.classList.add('exit');
      setTimeout(() => {
        current.classList.remove('active', 'exit');
      }, 350);
    }

    // Enter target
    target.classList.add('active');
    target.scrollTop = 0;
    currentScreen = targetId;

    // Update breadcrumb
    breadcrumb.textContent = screenLabels[targetId] || '🏠 Início';

    // Show/hide back button
    if (targetId === 'screen-home') {
      backBtn.classList.add('hidden');
    } else {
      backBtn.classList.remove('hidden');
    }

    resetInactivityTimer();
  }

  // Back button → Home
  backBtn.addEventListener('click', () => showScreen('screen-home'));
  backBtn.addEventListener('touchend', (e) => { e.preventDefault(); showScreen('screen-home'); });

  // Logo → Home
  logoBtn.addEventListener('click', () => showScreen('screen-home'));

  // Menu cards
  document.querySelectorAll('.menu-card[data-screen]').forEach(card => {
    card.addEventListener('click', () => {
      const target = card.getAttribute('data-screen');
      showScreen(target);
    });
  });


  // ==========================================================================
  // 3. TIMER DE INATIVIDADE (2 minutos → aviso → 10s → volta ao Home)
  // ==========================================================================
  const INACTIVITY_TIMEOUT_MS  = 2 * 60 * 1000; // 2 min sem toque
  const WARNING_COUNTDOWN_SEC  = 10;             // conta regressiva no overlay

  const inactivityOverlay  = document.getElementById('inactivity-overlay');
  const inactivityCountdown = document.getElementById('inactivity-countdown');
  const inactivityStayBtn  = document.getElementById('inactivity-stay-btn');

  let inactivityTimer    = null;
  let countdownTimer     = null;
  let countdownValue     = WARNING_COUNTDOWN_SEC;

  function resetInactivityTimer() {
    clearTimeout(inactivityTimer);
    clearInterval(countdownTimer);
    hideInactivityOverlay();

    // Only start timer if NOT on home screen (home screen can stay open indefinitely)
    if (currentScreen !== 'screen-home') {
      inactivityTimer = setTimeout(showInactivityWarning, INACTIVITY_TIMEOUT_MS);
    }
  }

  function showInactivityWarning() {
    countdownValue = WARNING_COUNTDOWN_SEC;
    inactivityCountdown.textContent = countdownValue;
    inactivityOverlay.classList.remove('hidden');

    countdownTimer = setInterval(() => {
      countdownValue--;
      inactivityCountdown.textContent = countdownValue;
      if (countdownValue <= 0) {
        clearInterval(countdownTimer);
        hideInactivityOverlay();
        showScreen('screen-home');
      }
    }, 1000);
  }

  function hideInactivityOverlay() {
    inactivityOverlay.classList.add('hidden');
    clearInterval(countdownTimer);
  }

  inactivityStayBtn.addEventListener('click', () => {
    hideInactivityOverlay();
    resetInactivityTimer();
  });

  // Listen for any user interaction to reset timer
  ['click', 'touchstart', 'touchend', 'mousemove', 'keydown'].forEach(evt => {
    document.addEventListener(evt, () => {
      if (!inactivityOverlay.classList.contains('hidden')) return; // don't reset mid-countdown from idle events
      resetInactivityTimer();
    }, { passive: true });
  });


  // ==========================================================================
  // 4. RENDERIZAR HORÁRIO DOS PROFESSORES (a partir de dados_escola.js)
  // ==========================================================================
  const horariosContainer = document.getElementById('horarios-container');
  const filterBtns = document.querySelectorAll('.btn-filter');
  let currentHorariosFilter = 'dia';

  if (filterBtns) {
    filterBtns.forEach(btn => {
      btn.addEventListener('click', (e) => {
        filterBtns.forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        currentHorariosFilter = e.target.getAttribute('data-filter');
        renderHorarios();
      });
    });
  }

  function renderHorarios() {
    if (!horariosContainer || typeof DADOS_ESCOLA === 'undefined') return;
    const profs = DADOS_ESCOLA.horarioProfessores;
    horariosContainer.innerHTML = '';
    const orderDias = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira"];

    function normKey(str) {
      if (!str) return '';
      return str.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/[^a-z]/g, "");
    }

    function findDiaCanonical(rawDia) {
      const k = normKey(rawDia);
      return orderDias.find(d => normKey(d) === k) || rawDia;
    }

    function getDiaIndex(rawDia) {
      const k = normKey(rawDia);
      const idx = orderDias.findIndex(d => normKey(d) === k);
      return idx >= 0 ? idx : 99;
    }

    function getClassesCount(horariosArr) {
      let totalMins = 0;
      horariosArr.forEach(h => {
        const [startH, startM] = h.inicio.split(':').map(Number);
        const [endH, endM] = h.fim.split(':').map(Number);
        totalMins += ((endH * 60 + endM) - (startH * 60 + startM));
      });
      return Math.round(totalMins / 50);
    }

    const profsMap = {};
    profs.forEach(p => profsMap[p.nome] = getClassesCount(p.horarios));

    function appendCardAndEvents(card, idx) {
      horariosContainer.appendChild(card);
      const header   = card.querySelector('.prof-card-header');
      const schedule = card.querySelector('.prof-schedule');

      if (idx === 0) {
        card.classList.add('open');
        requestAnimationFrame(() => {
          schedule.style.maxHeight = schedule.scrollHeight + 'px';
        });
      }

      header.addEventListener('click', () => {
        const isOpen = card.classList.contains('open');
        horariosContainer.querySelectorAll('.prof-card').forEach(c => {
          c.classList.remove('open');
          c.querySelector('.prof-schedule').style.maxHeight = '0';
        });
        if (!isOpen) {
          card.classList.add('open');
          schedule.style.maxHeight = schedule.scrollHeight + 'px';
        }
      });
    }

    if (currentHorariosFilter === 'dia') {
      const grouped = {};
      orderDias.forEach(d => grouped[d] = []);

      profs.forEach(prof => {
        prof.horarios.forEach(h => {
          const diaCanon = findDiaCanonical(h.dia);
          if (!grouped[diaCanon]) grouped[diaCanon] = [];
          grouped[diaCanon].push({
            profNome: prof.nome,
            disciplinas: prof.disciplinas.join(' • '),
            inicio: h.inicio,
            fim: h.fim,
            local: h.local
          });
        });
      });

      orderDias.forEach((dia, idx) => {
        const aulas = grouped[dia];
        if (!aulas || aulas.length === 0) return;
        aulas.sort((a, b) => a.inicio.localeCompare(b.inicio));

        const card = document.createElement('div');
        card.className = 'prof-card';
        card.innerHTML = `
          <div class="prof-card-header" data-idx="${idx}">
            <div class="prof-avatar" style="font-size: 24px;">📅</div>
            <div class="prof-info">
              <div class="prof-name">${dia}</div>
              <div class="prof-disciplines">${aulas.length} horário(s) disponível(is)</div>
            </div>
            <div class="prof-toggle">▼</div>
          </div>
          <div class="prof-schedule">
            <div class="prof-schedule-inner agenda-daily-grid">
              ${aulas.map(a => `
                <div class="agenda-card">
                  <div class="agenda-card-time">🕐 ${a.inicio} – ${a.fim}</div>
                  <div class="agenda-card-title">👩‍🏫 ${a.profNome} <span style="font-size:11px; font-weight:normal; color:var(--text-muted);">(${profsMap[a.profNome]}h/a)</span></div>
                  <div class="agenda-card-subtitle">${a.disciplinas}</div>
                  <div class="agenda-card-local">📍 ${a.local}</div>
                </div>
              `).join('')}
            </div>
          </div>
        `;
        appendCardAndEvents(card, idx);
      });

    } else if (currentHorariosFilter === 'professor') {
      const cleanName = (name) => name.replace(/^(Prof(?:[ºª]\.?|\.[ºª]?|\.)?\s*)/i, '').trim();
      const sortedProfs = [...profs].sort((a, b) => cleanName(a.nome).localeCompare(cleanName(b.nome)));
      
      sortedProfs.forEach((prof, idx) => {
        const initials = cleanName(prof.nome).charAt(0).toUpperCase();
        const avatarContent = prof.foto 
          ? `<img src="${prof.foto}" alt="${prof.nome}" style="width:100%;height:100%;object-fit:cover;border-radius:50%;">` 
          : `${initials}👩‍🏫`;

        const horariosSort = [...prof.horarios].sort((a, b) => {
          const idxA = getDiaIndex(a.dia);
          const idxB = getDiaIndex(b.dia);
          if (idxA !== idxB) return idxA - idxB;
          return a.inicio.localeCompare(b.inicio);
        });

        const card = document.createElement('div');
        card.className = 'prof-card';
        card.innerHTML = `
          <div class="prof-card-header" data-idx="${idx}">
            <div class="prof-avatar" style="padding: 0; overflow: hidden;">${avatarContent}</div>
            <div class="prof-info">
              <div class="prof-name">${prof.nome} <span style="font-size: 13px; color: var(--text-muted); font-weight: normal;">(${profsMap[prof.nome]}h/a)</span></div>
              <div class="prof-disciplines">${prof.disciplinas.join(' • ')}</div>
            </div>
            <div class="prof-toggle">▼</div>
          </div>
          <div class="prof-schedule">
            <div class="prof-schedule-inner agenda-weekly-grid">
              ${orderDias.map(dia => `
                <div class="agenda-col">
                  <div class="agenda-col-header">${dia.split('-')[0]}</div>
                  ${horariosSort.filter(h => normKey(h.dia) === normKey(dia)).map(h => `
                    <div class="agenda-card">
                      <div class="agenda-card-time">🕐 ${h.inicio} – ${h.fim}</div>
                      <div class="agenda-card-local" style="margin-top:2px;">📍 ${h.local}</div>
                    </div>
                  `).join('')}
                </div>
              `).join('')}
            </div>
          </div>
        `;
        appendCardAndEvents(card, idx);
      });

    } else if (currentHorariosFilter === 'disciplina') {
      const grouped = {};
      profs.forEach(prof => {
        prof.disciplinas.forEach(disc => {
          if (!grouped[disc]) grouped[disc] = [];
          prof.horarios.forEach(h => {
            grouped[disc].push({
              profNome: prof.nome,
              dia: h.dia,
              inicio: h.inicio,
              fim: h.fim,
              local: h.local
            });
          });
        });
      });
      
      const orderDisc = Object.keys(grouped).sort();
      
      orderDisc.forEach((disc, idx) => {
        const aulas = grouped[disc];
        aulas.sort((a, b) => {
          const idxA = getDiaIndex(a.dia);
          const idxB = getDiaIndex(b.dia);
          if (idxA !== idxB) return idxA - idxB;
          return a.inicio.localeCompare(b.inicio);
        });

        const card = document.createElement('div');
        card.className = 'prof-card';
        card.innerHTML = `
          <div class="prof-card-header" data-idx="${idx}">
            <div class="prof-avatar" style="font-size: 24px;">📚</div>
            <div class="prof-info">
              <div class="prof-name">${disc}</div>
              <div class="prof-disciplines">${aulas.length} horário(s) na semana</div>
            </div>
            <div class="prof-toggle">▼</div>
          </div>
          <div class="prof-schedule">
            <div class="prof-schedule-inner agenda-weekly-grid">
              ${orderDias.map(dia => `
                <div class="agenda-col">
                  <div class="agenda-col-header">${dia.split('-')[0]}</div>
                  ${aulas.filter(a => normKey(a.dia) === normKey(dia)).map(a => `
                    <div class="agenda-card">
                      <div class="agenda-card-time">🕐 ${a.inicio} – ${a.fim}</div>
                      <div class="agenda-card-title" style="margin-top: 4px;">👩‍🏫 ${a.profNome} <span style="font-size:11px; font-weight:normal; color:var(--text-muted);">(${profsMap[a.profNome]}h/a)</span></div>
                      <div class="agenda-card-local" style="margin-top: 4px;">📍 ${a.local}</div>
                    </div>
                  `).join('')}
                </div>
              `).join('')}
            </div>
          </div>
        `;
        appendCardAndEvents(card, idx);
      });
    }
  }




  // ==========================================================================
  // 5. RENDERIZAR MATRÍCULA (a partir de dados_escola.js)
  // ==========================================================================
  const matriculaContainer = document.getElementById('matricula-container');

  function renderMatricula() {
    if (!matriculaContainer || typeof DADOS_ESCOLA === 'undefined') return;
    const m = DADOS_ESCOLA.matricula;

    matriculaContainer.innerHTML = `
      <!-- Período -->
      <div class="matricula-card full-width">
        <h3><span class="m-icon">📅</span> Período de Matrícula</h3>
        <div class="matricula-period-badge">✅ ${m.periodo}</div>
        <p class="matricula-local">${m.observacao}</p>
      </div>

      <!-- Docs Novos -->
      <div class="matricula-card">
        <h3><span class="m-icon">📄</span> Documentos Necessários</h3>
        <ul class="matricula-doc-list">
          ${m.documentosNovos.map(d => `<li>${d}</li>`).join('')}
        </ul>
      </div>

      <!-- Horário Atendimento -->
      <div class="matricula-card">
        <h3><span class="m-icon">🕐</span> Horário de Atendimento</h3>
        ${m.horarioAtendimento.map(h => `
          <div class="matricula-horario-item">
            <strong>${h.dia}</strong>
            <span>${h.horario}</span>
          </div>
        `).join('')}
        <p class="matricula-local" style="margin-top:8px">📍 ${m.localAtendimento}</p>
        <a href="https://wa.me/55${m.telefone.replace(/\D/g,'')}" target="_blank" class="wpp-btn">
          💬 WhatsApp: ${m.telefone}
        </a>
      </div>

      <!-- Observações -->
      <div class="matricula-card">
        <h3><span class="m-icon">💡</span> Informações Importantes</h3>
        <ul class="matricula-obs-list">
          ${m.observacoes.map(o => `<li>${o}</li>`).join('')}
        </ul>
      </div>
    `;
  }



  // ==========================================================================
  // 6. RENDERIZAR DISCIPLINAS (a partir de dados_escola.js)
  // ==========================================================================
  const disciplinasContainer = document.getElementById('disciplinas-container');

  function renderDisciplinas() {
    if (!disciplinasContainer || typeof DADOS_ESCOLA === 'undefined') return;
    const areas = DADOS_ESCOLA.disciplinas;
    disciplinasContainer.innerHTML = '';

    areas.forEach(area => {
      const card = document.createElement('div');
      card.className = 'area-card';
      card.innerHTML = `
        <div class="area-card-header" style="border-bottom: 3px solid ${area.cor}20; background: ${area.cor}15;">
          <span class="area-icon">${area.icone}</span>
          <span class="area-title" style="color: ${area.cor};">${area.area}</span>
        </div>
        <div class="area-card-body">
          ${area.materias.map(mat => `
            <div class="materia-item">
              <span class="materia-nome">${mat.nome}</span>
            </div>
          `).join('')}
        </div>
      `;
      disciplinasContainer.appendChild(card);
    });
  }



  // ==========================================================================
  // 7. SIMULADOR DE NOTAS (Sliders)
  // ==========================================================================
  const rangeAv1 = document.getElementById('range-av1');
  const rangeAv2 = document.getElementById('range-av2');
  const rangeAv3 = document.getElementById('range-av3');
  const valAv1   = document.getElementById('val-av1');
  const valAv2   = document.getElementById('val-av2');
  const valAv3   = document.getElementById('val-av3');

  const resultPanel       = document.getElementById('result-panel');
  const resultGrade       = document.getElementById('result-grade');
  const resultStatus      = document.getElementById('result-status');
  const resultDesc        = document.getElementById('result-desc');
  const gaugeFillCircle   = document.getElementById('gauge-fill-circle');

  const GAUGE_CIRCUMFERENCE = 251.2;

  function updateSimulator() {
    const av1 = parseFloat(rangeAv1.value);
    const av2 = parseFloat(rangeAv2.value);
    const av3 = parseFloat(rangeAv3.value);

    valAv1.textContent = av1.toFixed(1);
    valAv2.textContent = av2.toFixed(1);
    valAv3.textContent = av3.toFixed(1);

    const media  = (av1 * 0.1) + (av2 * 0.2) + (av3 * 0.7);
    resultGrade.textContent = media.toFixed(1);

    const offset = GAUGE_CIRCUMFERENCE - (GAUGE_CIRCUMFERENCE * (media / 10));
    gaugeFillCircle.style.strokeDashoffset = offset;

    if (media >= 5.0) {
      resultPanel.className = 'sim-result result-approved';
      resultStatus.textContent = 'Aprovado! 🎉';
      resultDesc.innerHTML = `Média <strong>${media.toFixed(1)}</strong> — você alcançou a média mínima e está aprovado!`;
    } else {
      resultPanel.className = 'sim-result result-pending';
      resultStatus.textContent = 'Nota Pendente ⚠️';
      resultDesc.innerHTML = `Média <strong>${media.toFixed(1)}</strong> — precisa atingir <strong>5.0</strong> para aprovação.`;
    }
  }

  [rangeAv1, rangeAv2, rangeAv3].forEach(slider => {
    slider.addEventListener('input', updateSimulator);
    slider.addEventListener('change', updateSimulator);
  });

  updateSimulator();


  // ==========================================================================
  // 8. CALCULADORA DE META DA AV3
  // ==========================================================================
  const inputAv1       = document.getElementById('input-av1');
  const inputAv2       = document.getElementById('input-av2');
  const btnCalcTarget  = document.getElementById('btn-calc-target');
  const targetResultBox = document.getElementById('target-result-box');
  const targetText     = document.getElementById('target-text');

  btnCalcTarget.addEventListener('click', () => {
    const val1 = inputAv1.value.trim();
    const val2 = inputAv2.value.trim();

    targetResultBox.className = 'target-result';

    if (val1 === '' || val2 === '') {
      targetResultBox.classList.add('target-result-pending');
      targetText.innerHTML = '⚠️ Por favor, insira as notas da AV1 e da AV2 para calcular.';
      targetResultBox.classList.remove('hidden');
      return;
    }

    const av1 = parseFloat(val1);
    const av2 = parseFloat(val2);

    if (isNaN(av1) || isNaN(av2) || av1 < 0 || av1 > 10 || av2 < 0 || av2 > 10) {
      targetResultBox.classList.add('target-result-pending');
      targetText.innerHTML = '⚠️ Por favor, insira notas válidas entre 0 e 10.';
      targetResultBox.classList.remove('hidden');
      return;
    }

    const currentPoints = (av1 * 0.1) + (av2 * 0.2);
    const neededOnAv3   = (5.0 - currentPoints) / 0.7;

    targetResultBox.classList.remove('hidden');

    if (neededOnAv3 <= 0) {
      targetResultBox.classList.add('target-result-success');
      targetText.innerHTML = `<strong>Aprovado por Média! 🎉</strong><br>Suas notas na AV1 e AV2 já somam <strong>${currentPoints.toFixed(2)}</strong> pontos. Qualquer nota na AV3 garante sua aprovação. <em>(Lembre-se: a AV3 presencial continua sendo obrigatória!)</em>`;
    } else if (neededOnAv3 > 10) {
      const maxPossible = currentPoints + 7.0;
      targetResultBox.classList.add('target-result-pending');
      targetText.innerHTML = `<strong>Atenção! ⚠️</strong><br>Sua nota máxima possível seria <strong>${maxPossible.toFixed(1)}</strong> (tirando 10 na AV3). A média mínima de 5.0 não é mais alcançável. Procure seus professores para orientação.`;
    } else {
      targetResultBox.classList.add('target-result-success');
      targetText.innerHTML = `Para alcançar a média <strong>5.0</strong>, você precisa tirar no mínimo <strong>${neededOnAv3.toFixed(1)}</strong> na <strong>AV3 Presencial</strong>.`;
    }
  });


  // ==========================================================================
  // 9. FAQ ACCORDION
  // ==========================================================================
  document.querySelectorAll('.faq-question').forEach(question => {
    question.addEventListener('click', function () {
      const answer = this.nextElementSibling;

      // Close all others
      document.querySelectorAll('.faq-question').forEach(q => {
        if (q !== this && q.classList.contains('active')) {
          q.classList.remove('active');
          q.nextElementSibling.style.maxHeight = '0';
          q.nextElementSibling.style.padding   = '0 20px';
        }
      });

      this.classList.toggle('active');

      if (this.classList.contains('active')) {
        answer.style.maxHeight = answer.scrollHeight + 'px';
        answer.style.padding   = '12px 20px 16px';
      } else {
        answer.style.maxHeight = '0';
        answer.style.padding   = '0 20px';
      }
    });
  });


  // ==========================================================================
  // 10. FORMULÁRIO DE FEEDBACK ANÔNIMO
  // ==========================================================================
  const feedbackForm      = document.getElementById('feedback-form');
  const feedbackChips     = document.querySelectorAll('.feedback-chip');
  const feedbackTypeInput = document.getElementById('feedback-type');
  const feedbackTopic     = document.getElementById('feedback-topic');
  const feedbackMessage   = document.getElementById('feedback-message');
  const charCounter       = document.getElementById('char-counter');
  const feedbackSuccess   = document.getElementById('feedback-success');
  const btnNewFeedback    = document.getElementById('btn-new-feedback');

  feedbackChips.forEach(chip => {
    chip.addEventListener('click', () => {
      feedbackChips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      feedbackTypeInput.value = chip.getAttribute('data-type');
    });
  });

  feedbackMessage.addEventListener('input', () => {
    const length = feedbackMessage.value.length;
    charCounter.textContent = `${length} / 500`;
    charCounter.className = 'char-counter';
    if (length >= 450) charCounter.classList.add('limit');
    else if (length >= 400) charCounter.classList.add('warning');
  });

  feedbackForm.addEventListener('submit', (e) => {
    e.preventDefault();

    const type    = feedbackTypeInput.value;
    const topic   = feedbackTopic.value;
    const message = feedbackMessage.value.trim();

    if (message.length < 10) {
      alert('Sua mensagem é muito curta. Por favor, escreva pelo menos 10 caracteres.');
      return;
    }

    const newFeedback = {
      id: Date.now().toString(),
      timestamp: new Date().toLocaleString('pt-BR'),
      type, topic, message
    };

    const feedbacks = JSON.parse(localStorage.getItem('ceja_feedbacks') || '[]');
    feedbacks.push(newFeedback);
    localStorage.setItem('ceja_feedbacks', JSON.stringify(feedbacks));

    const submitBtn = feedbackForm.querySelector('.btn-submit-feedback');
    const originalBtnText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = 'Enviando de forma anônima... ⏳';

    const typeLabelMap = {
      sugestao: 'Sugestão 💡', reclamacao: 'Reclamação ⚠️',
      elogio: 'Elogio ⭐',     outro: 'Outro 💬'
    };
    const categoryName = typeLabelMap[type] || type;
    const emailSubject = `[CEJA Feedback] Novo envio: ${categoryName} (${topic})`;

    fetch('https://formsubmit.co/ajax/admcejamesquita@gmail.com', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify({
        _subject: emailSubject, _captcha: 'false', _template: 'box',
        'Tipo de Mensagem': categoryName, 'Assunto': topic, 'Mensagem': message,
        'Data/Hora de Envio': newFeedback.timestamp
      })
    })
    .catch(() => {}) // localStorage fallback is enough
    .finally(() => {
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalBtnText;
      feedbackForm.reset();
      feedbackChips.forEach(c => c.classList.remove('active'));
      feedbackChips[0].classList.add('active');
      feedbackTypeInput.value = 'sugestao';
      charCounter.textContent = '0 / 500';
      charCounter.className = 'char-counter';
      feedbackForm.classList.add('hidden');
      feedbackSuccess.classList.remove('hidden');
    });
  });

  btnNewFeedback.addEventListener('click', () => {
    feedbackSuccess.classList.add('hidden');
    feedbackForm.classList.remove('hidden');
  });


  // ==========================================================================
  // 11. PAINEL ADMIN
  // ==========================================================================
  const btnAdminPanel       = document.getElementById('btn-admin-panel');
  const adminModal          = document.getElementById('admin-modal');
  const btnCloseLogin       = document.getElementById('btn-close-login');
  const btnCloseDashboard   = document.getElementById('btn-close-dashboard');
  const adminModalBackdrop  = document.querySelector('.admin-modal-backdrop');

  const adminLoginScreen    = document.getElementById('admin-login-screen');
  const adminDashboardScreen = document.getElementById('admin-dashboard-screen');
  const adminLoginForm      = document.getElementById('admin-login-form');
  const adminPasswordInput  = document.getElementById('admin-password');
  const loginErrorMsg       = document.getElementById('login-error-msg');

  const adminFilterType     = document.getElementById('admin-filter-type');
  const adminFeedbackTbody = document.getElementById('admin-feedback-tbody');
  const noFeedbacksMsg      = document.getElementById('no-feedbacks-msg');
  const btnExportCsv        = document.getElementById('btn-export-csv');
  const btnClearAll         = document.getElementById('btn-clear-all');

  const btnFullscreen       = document.getElementById('btn-fullscreen');

  if (btnFullscreen) {
    btnFullscreen.addEventListener('click', () => {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(err => {
          alert(`Erro ao tentar entrar em tela cheia: ${err.message}`);
        });
      } else {
        document.exitFullscreen();
      }
    });
  }

  btnAdminPanel.addEventListener('click', () => {
    adminModal.classList.remove('hidden');
    adminLoginScreen.classList.remove('hidden');
    adminDashboardScreen.classList.add('hidden');
    loginErrorMsg.classList.add('hidden');
    adminPasswordInput.value = '';
    adminPasswordInput.focus();
  });

  function closeAdminModal() { adminModal.classList.add('hidden'); }

  [btnCloseLogin, btnCloseDashboard, adminModalBackdrop].forEach(el => {
    el.addEventListener('click', closeAdminModal);
  });

  adminLoginForm.addEventListener('submit', (e) => {
    e.preventDefault();
    if (adminPasswordInput.value === 'Lsd257996*') {
      loginErrorMsg.classList.add('hidden');
      adminLoginScreen.classList.add('hidden');
      adminDashboardScreen.classList.remove('hidden');
      renderAdminFeedbacks();
    } else {
      loginErrorMsg.classList.remove('hidden');
      adminPasswordInput.value = '';
      adminPasswordInput.focus();
    }
  });

  function escapeHtml(text) {
    return text.replace(/[&<>"']/g, m => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[m]));
  }

  function renderAdminFeedbacks() {
    const feedbacks = JSON.parse(localStorage.getItem('ceja_feedbacks') || '[]');
    const filter    = adminFilterType.value;
    const filtered  = feedbacks
      .filter(item => filter === 'todos' || item.type === filter)
      .sort((a, b) => b.id.localeCompare(a.id));

    adminFeedbackTbody.innerHTML = '';
    const table = document.querySelector('.admin-table');

    if (filtered.length === 0) {
      noFeedbacksMsg.classList.remove('hidden');
      table.classList.add('hidden');
    } else {
      noFeedbacksMsg.classList.add('hidden');
      table.classList.remove('hidden');

      const typeLabels = {
        sugestao: '💡 Sugestão', reclamacao: '⚠️ Reclamação',
        elogio: '⭐ Elogio',     outro: '💬 Outro'
      };

      filtered.forEach(item => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${item.timestamp}</td>
          <td><span class="badge-table ${item.type}">${typeLabels[item.type] || item.type}</span></td>
          <td>${escapeHtml(item.topic)}</td>
          <td>${escapeHtml(item.message)}</td>
          <td>
            <button class="btn-delete-item" data-id="${item.id}" title="Excluir">🗑️</button>
          </td>
        `;
        adminFeedbackTbody.appendChild(tr);
      });

      adminFeedbackTbody.querySelectorAll('.btn-delete-item').forEach(btn => {
        btn.addEventListener('click', function () {
          if (confirm('Deseja excluir esta mensagem permanentemente?')) {
            let fb = JSON.parse(localStorage.getItem('ceja_feedbacks') || '[]');
            fb = fb.filter(x => x.id !== this.getAttribute('data-id'));
            localStorage.setItem('ceja_feedbacks', JSON.stringify(fb));
            renderAdminFeedbacks();
          }
        });
      });
    }
  }

  adminFilterType.addEventListener('change', renderAdminFeedbacks);

  btnClearAll.addEventListener('click', () => {
    if (confirm('Atenção: Isso excluirá todas as mensagens permanentemente. Deseja continuar?')) {
      localStorage.removeItem('ceja_feedbacks');
      renderAdminFeedbacks();
    }
  });

  btnExportCsv.addEventListener('click', () => {
    const feedbacks = JSON.parse(localStorage.getItem('ceja_feedbacks') || '[]');
    if (feedbacks.length === 0) { alert('Não há dados para exportar.'); return; }

    const typeLabelMap = { sugestao: 'Sugestão', reclamacao: 'Reclamação', elogio: 'Elogio', outro: 'Outro' };
    let csv = '\uFEFF' + ['Data/Hora', 'Tipo', 'Assunto', 'Mensagem'].join(';') + '\n';
    feedbacks.forEach(item => {
      const row = [
        item.timestamp,
        typeLabelMap[item.type] || item.type,
        item.topic,
        item.message.replace(/"/g, '""')
      ].map(v => `"${v}"`).join(';');
      csv += row + '\n';
    });

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url  = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'feedbacks_ceja.csv';
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  });


  // ==========================================================================
  // PONTO ELETRÔNICO (TOTEM PÚBLICO) MODAL
  // ==========================================================================
  const btnPontoModal       = document.getElementById('btn-ponto-modal');
  const pontoModal          = document.getElementById('ponto-modal');
  const pontoModalBackdrop  = document.getElementById('ponto-modal-backdrop');
  const btnClosePontoPin    = document.getElementById('btn-close-ponto-pin');
  const btnClosePontoCamera = document.getElementById('btn-close-ponto-camera');

  const pontoScreenPin      = document.getElementById('ponto-screen-pin');
  const pontoScreenCamera   = document.getElementById('ponto-screen-camera');
  const pontoScreenSuccess  = document.getElementById('ponto-screen-success');

  const pontoFuncSelect     = document.getElementById('ponto-func-select');
  const pontoPinInput       = document.getElementById('ponto-pin-input');
  const pontoPinError       = document.getElementById('ponto-pin-error');
  const btnPontoPinBackspace= document.getElementById('btn-ponto-pin-backspace');
  const btnPontoPinClear    = document.getElementById('btn-ponto-pin-clear');
  const btnPontoPinSubmit   = document.getElementById('btn-ponto-pin-submit');

  const pontoFuncName       = document.getElementById('ponto-func-name');
  const pontoFuncInfo       = document.getElementById('ponto-func-info');
  const pontoWebcam         = document.getElementById('ponto-webcam');
  const pontoCanvas         = document.getElementById('ponto-canvas');
  const pontoCameraStatus   = document.getElementById('ponto-camera-status');

  const pontoResTipo        = document.getElementById('ponto-res-tipo');
  const pontoResNome        = document.getElementById('ponto-res-nome');
  const pontoResDataHora    = document.getElementById('ponto-res-data-hora');
  const pontoResEmail       = document.getElementById('ponto-res-email');
  const pontoSuccessCountdown = document.getElementById('ponto-success-countdown');
  const btnPontoFinish      = document.getElementById('btn-ponto-finish');

  let selectedFuncionarioId = null;
  let webcamStream = null;
  let pontoAutoCloseTimer = null;
  let pontoAutoCloseSecs = 5;

  async function carregarTerceirizadosTotem() {
    try {
      const resp = await fetch('/funcionarios/ponto/api/terceirizados/');
      const data = await resp.json();
      if (data.success && data.terceirizados) {
        pontoFuncSelect.innerHTML = '<option value="" selected disabled>-- Selecione seu Nome --</option>';
        data.terceirizados.forEach(f => {
          const opt = document.createElement('option');
          opt.value = f.id;
          opt.textContent = `${f.nome} — ${f.cargo} (${f.empresa})`;
          pontoFuncSelect.appendChild(opt);
        });
      }
    } catch (e) {
      console.warn("Erro ao carregar terceirizados:", e);
      pontoFuncSelect.innerHTML = '<option value="" selected disabled>Erro ao carregar lista de funcionários</option>';
    }
  }

  window.abrirPontoModal = function(e) {
    if (e && e.preventDefault) e.preventDefault();
    if (pontoModal) pontoModal.classList.remove('hidden');
    if (pontoScreenPin) pontoScreenPin.classList.remove('hidden');
    if (pontoScreenCamera) pontoScreenCamera.classList.add('hidden');
    if (pontoScreenSuccess) pontoScreenSuccess.classList.add('hidden');
    if (pontoPinError) pontoPinError.classList.add('hidden');
    if (pontoPinInput) pontoPinInput.value = '';
    carregarTerceirizadosTotem();
  };

  window.fecharPontoModal = function() {
    if (pontoModal) pontoModal.classList.add('hidden');
    pararWebcamPonto();
    if (pontoAutoCloseTimer) clearInterval(pontoAutoCloseTimer);
  };

  if (btnPontoModal) {
    btnPontoModal.addEventListener('click', window.abrirPontoModal);
    btnPontoModal.addEventListener('touchend', window.abrirPontoModal);
  }

  [btnClosePontoPin, btnClosePontoCamera, pontoModalBackdrop, btnPontoFinish].forEach(el => {
    if (el) {
      el.addEventListener('click', window.fecharPontoModal);
      el.addEventListener('touchend', window.fecharPontoModal);
    }
  });

  document.querySelectorAll('.btn-ponto-key[data-key]').forEach(btn => {
    btn.addEventListener('click', () => {
      if (pontoPinInput.value.length < 12) {
        pontoPinInput.value += btn.getAttribute('data-key');
      }
    });
  });

  if (btnPontoPinBackspace) {
    btnPontoPinBackspace.addEventListener('click', () => {
      pontoPinInput.value = pontoPinInput.value.slice(0, -1);
    });
  }

  if (btnPontoPinClear) {
    btnPontoPinClear.addEventListener('click', () => {
      pontoPinInput.value = '';
    });
  }

  async function validarPinTotem() {
    const pin = pontoPinInput ? pontoPinInput.value.trim() : '';

    if (!pin) {
      if (pontoPinError) {
        pontoPinError.textContent = '⚠️ Por favor, digite a sua senha de ponto (PIN).';
        pontoPinError.classList.remove('hidden');
      }
      return;
    }

    const formData = new FormData();
    formData.append('pin', pin);

    try {
      const resp = await fetch('/funcionarios/ponto/api/validar_pin/', {
        method: 'POST',
        body: formData
      });
      const data = await resp.json();

      if (data.success) {
        if (pontoPinError) pontoPinError.classList.add('hidden');
        selectedFuncionarioId = data.funcionario_id;
        if (pontoFuncName) pontoFuncName.textContent = `👤 ${data.nome}`;
        if (pontoFuncInfo) pontoFuncInfo.textContent = `${data.cargo} — ${data.empresa}`;

        if (pontoScreenPin) pontoScreenPin.classList.add('hidden');
        if (pontoScreenCamera) pontoScreenCamera.classList.remove('hidden');
        iniciarWebcamPonto();
      } else {
        if (pontoPinError) {
          pontoPinError.textContent = `⚠️ ${data.error}`;
          pontoPinError.classList.remove('hidden');
        }
      }
    } catch (err) {
      console.error(err);
      if (pontoPinError) {
        pontoPinError.textContent = '⚠️ Erro ao conectar ao servidor. Tente novamente.';
        pontoPinError.classList.remove('hidden');
      }
    }
  }

  if (btnPontoPinSubmit) {
    btnPontoPinSubmit.addEventListener('click', validarPinTotem);
    btnPontoPinSubmit.addEventListener('touchend', validarPinTotem);
  }

  async function iniciarWebcamPonto() {
    try {
      webcamStream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480, facingMode: 'user' },
        audio: false
      });
      pontoWebcam.srcObject = webcamStream;
      pontoCameraStatus.textContent = 'Câmera Ativa';
      pontoCameraStatus.style.background = 'rgba(34,197,94,0.2)';
      pontoCameraStatus.style.color = '#4ade80';
    } catch (err) {
      console.warn("Câmera indisponível no totem:", err);
      pontoCameraStatus.textContent = 'Sem Câmera';
      pontoCameraStatus.style.background = 'rgba(234,179,8,0.2)';
      pontoCameraStatus.style.color = '#facc15';
    }
  }

  function pararWebcamPonto() {
    if (webcamStream) {
      webcamStream.getTracks().forEach(track => track.stop());
      webcamStream = null;
    }
  }

  function capturarFotoPonto() {
    if (!pontoWebcam.srcObject) return '';
    try {
      pontoCanvas.width = pontoWebcam.videoWidth || 640;
      pontoCanvas.height = pontoWebcam.videoHeight || 480;
      const ctx = pontoCanvas.getContext('2d');
      ctx.drawImage(pontoWebcam, 0, 0, pontoCanvas.width, pontoCanvas.height);
      return pontoCanvas.toDataURL('image/jpeg', 0.85);
    } catch (e) {
      return '';
    }
  }

  document.querySelectorAll('.btn-ponto-action').forEach(btn => {
    btn.addEventListener('click', async () => {
      const tipo = btn.getAttribute('data-tipo');
      const pin = pontoPinInput.value;
      const fotoBase64 = capturarFotoPonto();

      const formData = new FormData();
      formData.append('funcionario_id', selectedFuncionarioId);
      formData.append('pin', pin);
      formData.append('tipo', tipo);
      formData.append('foto_base64', fotoBase64);

      try {
        const resp = await fetch('/funcionarios/ponto/api/registrar/', {
          method: 'POST',
          body: formData
        });
        const data = await resp.json();

        if (data.success) {
          pararWebcamPonto();
          pontoResTipo.textContent = `${data.tipo.toUpperCase()} REGISTRADA`;
          pontoResNome.textContent = data.funcionario;
          pontoResDataHora.textContent = data.data_hora;
          pontoResEmail.textContent = `Comprovante enviado para: ${data.email_destinatario}`;

          pontoScreenCamera.classList.add('hidden');
          pontoScreenSuccess.classList.remove('hidden');

          pontoAutoCloseSecs = 5;
          pontoSuccessCountdown.textContent = pontoAutoCloseSecs;
          if (pontoAutoCloseTimer) clearInterval(pontoAutoCloseTimer);
          pontoAutoCloseTimer = setInterval(() => {
            pontoAutoCloseSecs--;
            pontoSuccessCountdown.textContent = pontoAutoCloseSecs;
            if (pontoAutoCloseSecs <= 0) {
              fecharPontoModal();
            }
          }, 1000);

        } else {
          alert('ERRO: ' + data.error);
        }
      } catch (err) {
        console.error(err);
        alert('Erro ao conectar ao servidor para registrar o ponto.');
      }
    });
  });


  // ==========================================================================
  // INICIALIZAÇÃO
  // ==========================================================================
  resetInactivityTimer();

});

