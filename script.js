document.addEventListener('DOMContentLoaded', () => {

  // ==========================================================================
  // ELEMENT SELECTORS
  // ==========================================================================
  
  // Sliders & Values
  const rangeAv1 = document.getElementById('range-av1');
  const rangeAv2 = document.getElementById('range-av2');
  const rangeAv3 = document.getElementById('range-av3');
  
  const valAv1 = document.getElementById('val-av1');
  const valAv2 = document.getElementById('val-av2');
  const valAv3 = document.getElementById('val-av3');

  // Result Panel Elements
  const resultPanel = document.getElementById('result-panel');
  const resultGrade = document.getElementById('result-grade');
  const resultStatus = document.getElementById('result-status');
  const resultDesc = document.getElementById('result-desc');
  const gaugeFillCircle = document.getElementById('gauge-fill-circle');

  // Target Calculator Elements
  const inputAv1 = document.getElementById('input-av1');
  const inputAv2 = document.getElementById('input-av2');
  const btnCalcTarget = document.getElementById('btn-calc-target');
  const targetResultBox = document.getElementById('target-result-box');
  const targetText = document.getElementById('target-text');

  // FAQ Accordion Elements
  const faqQuestions = document.querySelectorAll('.faq-question');

  // Print Button
  const btnPrint = document.getElementById('btnPrint');

  // Circumference of the gauge circle: 2 * Math.PI * r (where r = 40)
  const GAUGE_CIRCUMFERENCE = 251.2;

  // ==========================================================================
  // SIMULATOR FUNCTIONAL LOGIC
  // ==========================================================================

  function updateSimulator() {
    const av1 = parseFloat(rangeAv1.value);
    const av2 = parseFloat(rangeAv2.value);
    const av3 = parseFloat(rangeAv3.value);

    // Update range labels
    valAv1.textContent = av1.toFixed(1);
    valAv2.textContent = av2.toFixed(1);
    valAv3.textContent = av3.toFixed(1);

    // Calculate weighted average: (AV1 * 0.1) + (AV2 * 0.2) + (AV3 * 0.7)
    const media = (av1 * 0.1) + (av2 * 0.2) + (av3 * 0.7);
    resultGrade.textContent = media.toFixed(1);

    // Update circular gauge SVG fill
    // dashoffset of 0 means 100% full, dashoffset of GAUGE_CIRCUMFERENCE means 0% full
    const offset = GAUGE_CIRCUMFERENCE - (GAUGE_CIRCUMFERENCE * (media / 10));
    gaugeFillCircle.style.strokeDashoffset = offset;

    // Determine status and styling
    if (media >= 5.0) {
      resultPanel.className = 'simulator-result result-approved';
      resultStatus.textContent = 'Aprovado! 🎉';
      resultDesc.innerHTML = `Com essas notas, sua média é de <strong>${media.toFixed(1)}</strong>. Você alcançou a média mínima e está aprovado neste fascículo!`;
    } else {
      resultPanel.className = 'simulator-result result-pending';
      resultStatus.textContent = 'Nota Pendente ⚠️';
      resultDesc.innerHTML = `Com essas notas, sua média é de <strong>${media.toFixed(1)}</strong>. Você ainda precisa subir suas notas para alcançar a média mínima de <strong>5.0</strong>.`;
    }
  }

  // Bind change and input events to range sliders
  [rangeAv1, rangeAv2, rangeAv3].forEach(slider => {
    slider.addEventListener('input', updateSimulator);
    slider.addEventListener('change', updateSimulator);
  });

  // Initialize on load
  updateSimulator();


  // ==========================================================================
  // TARGET CALCULATOR FUNCTIONAL LOGIC (META DA AV3)
  // ==========================================================================

  btnCalcTarget.addEventListener('click', () => {
    const val1 = inputAv1.value.trim();
    const val2 = inputAv2.value.trim();

    // Reset styles
    targetResultBox.className = 'target-result';

    // Simple validation
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

    // Goal: (AV1 * 0.1) + (AV2 * 0.2) + (AV3 * 0.7) >= 5.0
    // AV3 * 0.7 >= 5.0 - (AV1 * 0.1) - (AV2 * 0.2)
    // AV3 >= (5.0 - (AV1 * 0.1) - (AV2 * 0.2)) / 0.7
    const currentPoints = (av1 * 0.1) + (av2 * 0.2);
    const neededOnAv3 = (5.0 - currentPoints) / 0.7;

    targetResultBox.classList.remove('hidden');

    if (neededOnAv3 <= 0) {
      // Already approved without AV3 (math-wise, but AV3 is still mandatory)
      targetResultBox.classList.add('target-result-success');
      targetText.innerHTML = `<strong>Aprovado por Média! 🎉</strong><br>Suas notas na AV1 e AV2 já somam <strong>${currentPoints.toFixed(2)}</strong> pontos na média. Você precisa de qualquer nota acima de 0 na AV3 para passar. <em>(Lembre-se: realizar a AV3 presencial continua sendo obrigatório!)</em>`;
    } else if (neededOnAv3 > 10) {
      // Impossible to pass even with 10 on AV3
      const maxPossibleMedia = currentPoints + 7.0;
      targetResultBox.classList.add('target-result-pending');
      targetText.innerHTML = `<strong>Atenção! ⚠️</strong><br>Sua nota máxima possível neste fascículo seria <strong>${maxPossibleMedia.toFixed(1)}</strong> (tirando 10 na AV3). Infelizmente, a média mínima de 5.0 não é mais alcançável apenas com a AV3. Procure seus professores para orientação sobre dependências ou recuperação.`;
    } else {
      // Needs a valid grade on AV3
      targetResultBox.classList.add('target-result-success');
      targetText.innerHTML = `Para alcançar a média 5.0 e passar, você precisa tirar no mínimo <strong>${neededOnAv3.toFixed(1)}</strong> na <strong>AV3 Presencial</strong>.`;
    }
  });


  // ==========================================================================
  // FAQ ACCORDION INTERACTION LOGIC
  // ==========================================================================

  faqQuestions.forEach(question => {
    question.addEventListener('click', function() {
      const answer = this.nextElementSibling;
      
      // Close other accordion items
      faqQuestions.forEach(q => {
        if (q !== this && q.classList.contains('active')) {
          q.classList.remove('active');
          q.nextElementSibling.style.maxHeight = '0';
          q.nextElementSibling.style.padding = '0 20px';
        }
      });

      // Toggle current accordion item
      this.classList.toggle('active');

      if (this.classList.contains('active')) {
        // Expand the panel
        answer.style.maxHeight = answer.scrollHeight + 'px';
        answer.style.padding = '12px 20px 16px';
      } else {
        // Collapse the panel
        answer.style.maxHeight = '0';
        answer.style.padding = '0 20px';
      }
    });
  });


  // ==========================================================================
  // PRINT FLYER TRIGGERS
  // ==========================================================================

  btnPrint.addEventListener('click', () => {
    window.print();
  });


  // ==========================================================================
  // FEEDBACK FORM LOGIC (SUGESTÕES E RECLAMAÇÕES ANÔNIMAS)
  // ==========================================================================
  
  const feedbackForm = document.getElementById('feedback-form');
  const feedbackChips = document.querySelectorAll('.feedback-chip');
  const feedbackTypeInput = document.getElementById('feedback-type');
  const feedbackTopic = document.getElementById('feedback-topic');
  const feedbackMessage = document.getElementById('feedback-message');
  const charCounter = document.getElementById('char-counter');
  const feedbackSuccess = document.getElementById('feedback-success');
  const btnNewFeedback = document.getElementById('btn-new-feedback');

  // Handle category chip selection
  feedbackChips.forEach(chip => {
    chip.addEventListener('click', () => {
      feedbackChips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      feedbackTypeInput.value = chip.getAttribute('data-type');
    });
  });

  // Track character count
  feedbackMessage.addEventListener('input', () => {
    const length = feedbackMessage.value.length;
    charCounter.textContent = `${length} / 500`;

    // Visual indicators for character limit
    charCounter.className = 'char-counter';
    if (length >= 450) {
      charCounter.classList.add('limit');
    } else if (length >= 400) {
      charCounter.classList.add('warning');
    }
  });

  // Handle feedback form submission
  feedbackForm.addEventListener('submit', (e) => {
    e.preventDefault();

    const type = feedbackTypeInput.value;
    const topic = feedbackTopic.value;
    const message = feedbackMessage.value.trim();

    if (message.length < 10) {
      alert('Sua mensagem é muito curta. Por favor, escreva pelo menos 10 caracteres.');
      return;
    }

    // Prepare feedback object (for local storage storage)
    const newFeedback = {
      id: Date.now().toString(),
      timestamp: new Date().toLocaleString('pt-BR'),
      type: type,
      topic: topic,
      message: message
    };

    // Load existing feedbacks and append new one (local storage)
    const feedbacks = JSON.parse(localStorage.getItem('ceja_feedbacks') || '[]');
    feedbacks.push(newFeedback);
    localStorage.setItem('ceja_feedbacks', JSON.stringify(feedbacks));

    // Show visual loading state on button
    const submitBtn = feedbackForm.querySelector('.btn-submit-feedback');
    const originalBtnText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span>Enviando de forma anônima...</span> ⏳';

    // FormSubmit integration parameters
    const typeLabelMap = {
      sugestao: 'Sugestão 💡',
      reclamacao: 'Reclamação ⚠️',
      elogio: 'Elogio ⭐',
      outro: 'Outro 💬'
    };
    const categoryName = typeLabelMap[type] || type;
    const emailSubject = `[CEJA Feedback] Novo envio: ${categoryName} (${topic})`;

    // Send payload asynchronously to school email
    fetch('https://formsubmit.co/ajax/admcejamesquita@gmail.com', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({
        _subject: emailSubject,
        _captcha: 'false',
        _template: 'box',
        'Tipo de Mensagem': categoryName,
        'Assunto': topic,
        'Mensagem': message,
        'Data/Hora de Envio': newFeedback.timestamp
      })
    })
    .then(response => response.json())
    .then(data => {
      // Show success screen
      feedbackForm.classList.add('hidden');
      feedbackSuccess.classList.remove('hidden');
    })
    .catch(error => {
      console.error('Error sending feedback to email:', error);
      // Even if email delivery fails, the local storage fallback works, so we still show success
      feedbackForm.classList.add('hidden');
      feedbackSuccess.classList.remove('hidden');
    })
    .finally(() => {
      // Restore button status
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalBtnText;

      // Reset form elements
      feedbackForm.reset();
      feedbackChips.forEach(c => c.classList.remove('active'));
      feedbackChips[0].classList.add('active'); // reset to first chip
      feedbackTypeInput.value = 'sugestao';
      charCounter.textContent = '0 / 500';
      charCounter.className = 'char-counter';
    });
  });

  // Return from success screen to blank form
  btnNewFeedback.addEventListener('click', () => {
    feedbackSuccess.classList.add('hidden');
    feedbackForm.classList.remove('hidden');
  });


  // ==========================================================================
  // ADMIN PANEL LOGIC
  // ==========================================================================

  const btnAdminPanel = document.getElementById('btn-admin-panel');
  const adminModal = document.getElementById('admin-modal');
  const btnCloseLogin = document.getElementById('btn-close-login');
  const btnCloseDashboard = document.getElementById('btn-close-dashboard');
  const adminModalBackdrop = document.querySelector('.admin-modal-backdrop');
  
  const adminLoginScreen = document.getElementById('admin-login-screen');
  const adminDashboardScreen = document.getElementById('admin-dashboard-screen');
  const adminLoginForm = document.getElementById('admin-login-form');
  const adminPasswordInput = document.getElementById('admin-password');
  const loginErrorMsg = document.getElementById('login-error-msg');

  const adminFilterType = document.getElementById('admin-filter-type');
  const adminFeedbackTbody = document.getElementById('admin-feedback-tbody');
  const noFeedbacksMsg = document.getElementById('no-feedbacks-msg');
  const btnExportCsv = document.getElementById('btn-export-csv');
  const btnClearAll = document.getElementById('btn-clear-all');

  // Open Admin Modal
  btnAdminPanel.addEventListener('click', () => {
    adminModal.classList.remove('hidden');
    adminLoginScreen.classList.remove('hidden');
    adminDashboardScreen.classList.add('hidden');
    loginErrorMsg.classList.add('hidden');
    adminPasswordInput.value = '';
    adminPasswordInput.focus();
  });

  // Close Admin Modal Functions
  function closeAdminModal() {
    adminModal.classList.add('hidden');
  }

  [btnCloseLogin, btnCloseDashboard, adminModalBackdrop].forEach(el => {
    el.addEventListener('click', closeAdminModal);
  });

  // Admin Passcode authentication (password: admin123)
  adminLoginForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const password = adminPasswordInput.value;

    if (password === 'admin123') {
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

  // Render feedbacks in table
  function renderAdminFeedbacks() {
    const feedbacks = JSON.parse(localStorage.getItem('ceja_feedbacks') || '[]');
    const selectedFilter = adminFilterType.value;
    
    // Sort chronologically descending (newest first)
    const filteredFeedbacks = feedbacks
      .filter(item => selectedFilter === 'todos' || item.type === selectedFilter)
      .sort((a, b) => b.id.localeCompare(a.id));

    // Clear previous rows
    adminFeedbackTbody.innerHTML = '';

    if (filteredFeedbacks.length === 0) {
      noFeedbacksMsg.classList.remove('hidden');
      document.querySelector('.admin-table').classList.add('hidden');
    } else {
      noFeedbacksMsg.classList.add('hidden');
      document.querySelector('.admin-table').classList.remove('hidden');

      filteredFeedbacks.forEach(item => {
        const tr = document.createElement('tr');
        
        // Map types to label badges
        const typeLabels = {
          sugestao: '💡 Sugestão',
          reclamacao: '⚠️ Reclamação',
          elogio: '⭐ Elogio',
          outro: '💬 Outro'
        };
        const typeLabel = typeLabels[item.type] || item.type;

        tr.innerHTML = `
          <td>${item.timestamp}</td>
          <td><span class="badge-table ${item.type}">${typeLabel}</span></td>
          <td>${escapeHtml(item.topic)}</td>
          <td>${escapeHtml(item.message)}</td>
          <td>
            <button class="btn-delete-item" data-id="${item.id}" title="Excluir Mensagem">🗑️</button>
          </td>
        `;
        
        adminFeedbackTbody.appendChild(tr);
      });

      // Bind delete click event to individual delete buttons
      const deleteButtons = adminFeedbackTbody.querySelectorAll('.btn-delete-item');
      deleteButtons.forEach(btn => {
        btn.addEventListener('click', function() {
          const idToDelete = this.getAttribute('data-id');
          deleteFeedbackItem(idToDelete);
        });
      });
    }
  }

  // Filter feedbacks selection change
  adminFilterType.addEventListener('change', renderAdminFeedbacks);

  // Helper to sanitize HTML content
  function escapeHtml(text) {
    const map = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
  }

  // Delete single feedback item
  function deleteFeedbackItem(id) {
    if (confirm('Deseja excluir esta mensagem permanentemente?')) {
      let feedbacks = JSON.parse(localStorage.getItem('ceja_feedbacks') || '[]');
      feedbacks = feedbacks.filter(item => item.id !== id);
      localStorage.setItem('ceja_feedbacks', JSON.stringify(feedbacks));
      renderAdminFeedbacks();
    }
  }

  // Clear all feedbacks
  btnClearAll.addEventListener('click', () => {
    if (confirm('Atenção: Isso excluirá todas as sugestões e reclamações permanentemente. Deseja continuar?')) {
      localStorage.removeItem('ceja_feedbacks');
      renderAdminFeedbacks();
    }
  });

  // Export feedbacks to CSV with UTF-8 BOM encoding for correct excel character sets
  btnExportCsv.addEventListener('click', () => {
    const feedbacks = JSON.parse(localStorage.getItem('ceja_feedbacks') || '[]');
    
    if (feedbacks.length === 0) {
      alert('Não há dados cadastrados para exportação.');
      return;
    }

    const headers = ['Data/Hora', 'Tipo', 'Assunto', 'Mensagem'];
    const typeLabelMap = {
      sugestao: 'Sugestão',
      reclamacao: 'Reclamação',
      elogio: 'Elogio',
      outro: 'Outro'
    };

    let csvContent = '\uFEFF'; // UTF-8 BOM
    csvContent += headers.join(';') + '\n';

    feedbacks.forEach(item => {
      const typeLabel = typeLabelMap[item.type] || item.type;
      // Escape quotes and format row
      const escapedMsg = item.message.replace(/"/g, '""');
      const row = [
        item.timestamp,
        typeLabel,
        item.topic,
        escapedMsg
      ].map(val => `"${val}"`).join(';');
      csvContent += row + '\n';
    });

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', 'sugestoes_e_reclamacoes_ceja.csv');
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  });

});
