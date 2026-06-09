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

});
