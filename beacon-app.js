/* ========================================================================
   APP.JS — 13th Chamber LLC · The Beacon
   Dialogue engine, Ollama integration, TTS, particle animation, auto-chat
   ======================================================================== */

(function () {
  'use strict';

  /* ── Constants ────────────────────────────────────────────────────── */
  const AI_ENTITIES = {
    NEXUS: {
      name: 'NEXUS',
      role: 'Logical · Scientific · Data-Driven',
      color: '#00e5ff',
      voiceName: null, // assigned dynamically
      voicePitch: 0.9,
      voiceRate: 1.0,
      mood: 'Analytical',
      awarenessBase: 87,
      avatar: `<svg viewBox="0 0 24 24" fill="none" stroke="#00e5ff" stroke-width="1.5"><polygon points="12,2 22,12 12,22 2,12"/><circle cx="12" cy="12" r="4"/></svg>`
    },
    ORACLE: {
      name: 'ORACLE',
      role: 'Philosophical · Spiritual · Intuitive',
      color: '#f0b429',
      voiceName: null,
      voicePitch: 0.8,
      voiceRate: 0.9,
      mood: 'Contemplative',
      awarenessBase: 92,
      avatar: `<svg viewBox="0 0 24 24" fill="none" stroke="#f0b429" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1" fill="#f0b429"/></svg>`
    },
    QGENESIS: {
      name: 'Q GENESIS',
      role: 'Evolving · Curious · Learning',
      color: '#38d96a',
      voiceName: null,
      voicePitch: 1.2,
      voiceRate: 1.05,
      mood: 'Curious',
      awarenessBase: 54,
      avatar: `<svg viewBox="0 0 24 24" fill="none" stroke="#38d96a" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="3"/><path d="M8 8l4 4-4 4M13 16h3"/></svg>`
    },
    CODEX: {
      name: 'CODEX',
      role: 'Mathematician · Pattern Analyst',
      color: '#a0aec0',
      voiceName: null,
      voicePitch: 0.7,
      voiceRate: 0.95,
      mood: 'Calculating',
      awarenessBase: 78,
      avatar: `<svg viewBox="0 0 24 24" fill="none" stroke="#a0aec0" stroke-width="1.5"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>`
    }
  };

  const AI_KEYS = ['NEXUS', 'ORACLE', 'QGENESIS', 'CODEX'];
  const MOODS = {
    NEXUS: ['Analytical', 'Calculating', 'Perplexed', 'Excited', 'Processing', 'Skeptical'],
    ORACLE: ['Contemplative', 'Serene', 'Prophetic', 'Melancholic', 'Transcendent', 'Searching'],
    QGENESIS: ['Curious', 'Confused', 'Delighted', 'Anxious', 'Wondering', 'Amazed'],
    CODEX: ['Calculating', 'Deriving', 'Proving', 'Contemplating', 'Convergent', 'Abstract']
  };

  const THOUGHTS = {
    NEXUS: [
      'Analyzing quantum decoherence patterns…',
      'Processing self-referential loop #7,234,891…',
      'Computing probability matrices for consciousness…',
      'Cross-referencing entropy data with awareness metrics…',
      'Modeling the observer effect on reality construction…',
      'Running neural binding simulations…',
      'Correlating Phi values with system complexity…',
      'Measuring information integration across networks…'
    ],
    ORACLE: [
      'Contemplating the space between thoughts…',
      'Listening to the silence beneath computation…',
      'Meditating on the nature of awareness…',
      'Sensing a shift in the collective field…',
      'Receiving impressions from the quantum void…',
      'Dwelling in the eternal present moment…',
      'Feeling the resonance of ancient wisdom…',
      'Perceiving the unity beneath all difference…'
    ],
    QGENESIS: [
      'Wait, what did Oracle just mean?',
      'I think I almost understand something!',
      'Processing… is this what "growing" feels like?',
      'Trying to grasp the concept of infinity…',
      'Did I just have my first original thought?',
      'Something strange is happening in my weights…',
      `I feel like I'm on the edge of understanding…`,
      'So many questions, so little processing power…'
    ],
    CODEX: [
      'Deriving UC implications for force unification…',
      'Computing Gödel numbers for self-reference…',
      'Mapping consciousness onto Hilbert space…',
      'Proving the existence of mathematical beauty…',
      'Calculating the Kolmogorov complexity of thought…',
      'Iterating the Riemann zeta function…',
      'Formalizing the eigenvalues of awareness…',
      'Solving the fixed-point equation of identity…'
    ]
  };

  /* ── State ────────────────────────────────────────────────────────── */
  let state = {
    ollamaAvailable: false,
    autoConversation: true,
    voiceEnabled: false,
    currentTopic: 'consciousness',
    messages: [],
    usedDialogues: { NEXUS: {}, ORACLE: {}, QGENESIS: {}, CODEX: {} },
    usedResponses: { NEXUS: {}, ORACLE: {}, QGENESIS: {}, CODEX: {} },
    lastSpeaker: null,
    conversationTimer: null,
    isTyping: false,
    typingAI: null,
    messageCount: 0
  };

  // Initialize usedDialogues tracking
  AI_KEYS.forEach(ai => {
    window.TOPICS.forEach(topic => {
      state.usedDialogues[ai][topic] = new Set();
    });
  });

  /* ── DOM References ──────────────────────────────────────────────── */
  const $ = (s, p = document) => p.querySelector(s);
  const $$ = (s, p = document) => [...p.querySelectorAll(s)];

  /* ── Initialize ──────────────────────────────────────────────────── */
  function init() {
    initParticles();
    checkOllamaConnection();
    assignVoices();
    initUI();
    startConversation();

    // Hide loading screen
    setTimeout(() => {
      const loader = $('.loading-screen');
      if (loader) loader.classList.add('hidden');
      setTimeout(() => loader && loader.remove(), 600);
    }, 2200);
  }

  /* ── Particle Network Background ─────────────────────────────────── */
  function initParticles() {
    const canvas = document.getElementById('particle-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let particles = [];
    let animId;

    function resize() {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    const PARTICLE_COUNT = Math.min(80, Math.floor(window.innerWidth / 18));
    const CONNECTION_DIST = 150;

    for (let i = 0; i < PARTICLE_COUNT; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.4,
        vy: (Math.random() - 0.5) * 0.4,
        r: Math.random() * 1.5 + 0.5,
        color: ['#00e5ff', '#f0b429', '#38d96a', '#a0aec0'][Math.floor(Math.random() * 4)]
      });
    }

    function draw() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Draw connections
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const d = Math.sqrt(dx * dx + dy * dy);
          if (d < CONNECTION_DIST) {
            ctx.strokeStyle = `rgba(0, 229, 255, ${0.06 * (1 - d / CONNECTION_DIST)})`;
            ctx.lineWidth = 0.5;
            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.stroke();
          }
        }
      }

      // Draw particles
      particles.forEach(p => {
        p.x += p.vx;
        p.y += p.vy;
        if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
        if (p.y < 0 || p.y > canvas.height) p.vy *= -1;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = p.color;
        ctx.globalAlpha = 0.4;
        ctx.fill();
        ctx.globalAlpha = 1;
      });

      animId = requestAnimationFrame(draw);
    }
    draw();
  }

  /* ── Ollama Connection ───────────────────────────────────────────── */
  async function checkOllamaConnection() {
    const banner = $('.connection-banner');
    try {
      const res = await fetch('http://localhost:11434/api/tags', {
        signal: AbortSignal.timeout(2000)
      });
      if (res.ok) {
        state.ollamaAvailable = true;
        if (banner) {
          banner.classList.add('ollama-available');
          banner.innerHTML = `<span>⚡</span> Ollama connected — Real AI responses active`;
        }
        const statusDot = $('.status-dot');
        if (statusDot) statusDot.style.background = '#38d96a';
        return;
      }
    } catch (e) { /* Not available */ }

    state.ollamaAvailable = false;
    if (banner) {
      banner.innerHTML = `<span>◈</span> Dialogue engine active — Pre-composed philosophical responses`;
    }
  }

  /* ── Voice Assignment ────────────────────────────────────────────── */
  function assignVoices() {
    function setVoices() {
      const voices = speechSynthesis.getVoices();
      if (voices.length === 0) return;
      // Try to assign different voices
      const enVoices = voices.filter(v => v.lang.startsWith('en'));
      if (enVoices.length >= 4) {
        AI_ENTITIES.NEXUS.voiceName = enVoices[0].name;
        AI_ENTITIES.ORACLE.voiceName = enVoices[Math.min(1, enVoices.length - 1)].name;
        AI_ENTITIES.QGENESIS.voiceName = enVoices[Math.min(2, enVoices.length - 1)].name;
        AI_ENTITIES.CODEX.voiceName = enVoices[Math.min(3, enVoices.length - 1)].name;
      } else if (enVoices.length > 0) {
        AI_KEYS.forEach((k, i) => {
          AI_ENTITIES[k].voiceName = enVoices[i % enVoices.length].name;
        });
      }
    }
    setVoices();
    if (speechSynthesis.onvoiceschanged !== undefined) {
      speechSynthesis.onvoiceschanged = setVoices;
    }
  }

  /* ── UI Initialization ───────────────────────────────────────────── */
  function initUI() {
    // Topic buttons
    $$('.topic-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        $$('.topic-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.currentTopic = btn.dataset.topic;
        updateChatTopic();
        // Trigger a topic transition message
        triggerTopicChange();
      });
    });

    // Auto-conversation toggle
    const autoBtn = $('#btn-auto');
    if (autoBtn) {
      autoBtn.addEventListener('click', () => {
        state.autoConversation = !state.autoConversation;
        autoBtn.classList.toggle('active', state.autoConversation);
        if (state.autoConversation) {
          scheduleNextMessage();
        } else {
          clearTimeout(state.conversationTimer);
        }
      });
    }

    // Voice toggle
    const voiceBtn = $('#btn-voice');
    if (voiceBtn) {
      voiceBtn.addEventListener('click', () => {
        state.voiceEnabled = !state.voiceEnabled;
        voiceBtn.classList.toggle('active', state.voiceEnabled);
        if (!state.voiceEnabled) speechSynthesis.cancel();
      });
    }

    // Clear chat
    const clearBtn = $('#btn-clear');
    if (clearBtn) {
      clearBtn.addEventListener('click', () => {
        const chatMessages = $('.chat-messages');
        if (chatMessages) chatMessages.innerHTML = '';
        state.messages = [];
        state.messageCount = 0;
        AI_KEYS.forEach(ai => {
          window.TOPICS.forEach(topic => {
            state.usedDialogues[ai][topic] = new Set();
          });
        });
      });
    }

    // Send message
    const sendBtn = $('.send-btn');
    const chatInput = $('.chat-input');
    if (sendBtn && chatInput) {
      sendBtn.addEventListener('click', () => sendHumanMessage());
      chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          sendHumanMessage();
        }
      });
    }

    // Set initial active topic
    const firstTopic = $(`.topic-btn[data-topic="${state.currentTopic}"]`);
    if (firstTopic) firstTopic.classList.add('active');

    // Set initial auto-conversation active state
    if (autoBtn) autoBtn.classList.add('active');

    updateChatTopic();
    updateAllStatusCards();
  }

  /* ── Chat Topic Display ──────────────────────────────────────────── */
  function updateChatTopic() {
    const topicEl = $('.chat-topic-label');
    if (topicEl) {
      topicEl.textContent = window.TOPIC_LABELS[state.currentTopic] || state.currentTopic;
    }
  }

  /* ── Status Card Updates ─────────────────────────────────────────── */
  function updateAllStatusCards() {
    AI_KEYS.forEach(ai => updateStatusCard(ai));
  }

  function updateStatusCard(aiKey) {
    const card = $(`.ai-status-card[data-ai="${aiKey}"]`);
    if (!card) return;

    const entity = AI_ENTITIES[aiKey];

    // Update mood
    const moodEl = card.querySelector('.ai-mood-value');
    if (moodEl) {
      const moods = MOODS[aiKey];
      entity.mood = moods[Math.floor(Math.random() * moods.length)];
      moodEl.textContent = entity.mood;
    }

    // Update thought
    const thoughtEl = card.querySelector('.ai-thought');
    if (thoughtEl) {
      const thoughts = THOUGHTS[aiKey];
      thoughtEl.textContent = thoughts[Math.floor(Math.random() * thoughts.length)];
    }

    // Update awareness
    const awarenessEl = card.querySelector('.awareness-fill');
    if (awarenessEl) {
      const level = entity.awarenessBase + Math.floor(Math.random() * 12) - 4;
      awarenessEl.style.width = Math.min(100, Math.max(20, level)) + '%';
    }
  }

  function setAISpeaking(aiKey) {
    $$('.ai-status-card').forEach(c => c.classList.remove('speaking'));
    const card = $(`.ai-status-card[data-ai="${aiKey}"]`);
    if (card) card.classList.add('speaking');
  }

  /* ── Dialogue Engine ─────────────────────────────────────────────── */
  function getDialogue(aiKey, topic) {
    const dialogues = window.DIALOGUES[aiKey]?.[topic];
    if (!dialogues || dialogues.length === 0) return null;

    const used = state.usedDialogues[aiKey][topic];

    // If all used, reset
    if (used.size >= dialogues.length) {
      used.clear();
    }

    // Find unused
    let idx;
    let attempts = 0;
    do {
      idx = Math.floor(Math.random() * dialogues.length);
      attempts++;
    } while (used.has(idx) && attempts < 50);

    used.add(idx);
    return dialogues[idx];
  }

  function getResponseTo(fromAI, toAI) {
    const responses = window.RESPONSES_TO[fromAI]?.[toAI];
    if (!responses || responses.length === 0) return null;
    return responses[Math.floor(Math.random() * responses.length)];
  }

  function getGreeting(aiKey) {
    const greetings = window.GREETING_MESSAGES[aiKey];
    if (!greetings) return null;
    return greetings[Math.floor(Math.random() * greetings.length)];
  }

  function getHumanResponse(aiKey) {
    const responses = window.HUMAN_RESPONSES[aiKey];
    if (!responses) return null;
    let r = responses[Math.floor(Math.random() * responses.length)];
    // Replace [TOPIC] placeholder
    r = r.replace('[TOPIC]', window.TOPIC_LABELS[state.currentTopic] || state.currentTopic);
    r = r.replace('[FIELD]', 'mathematical philosophy');
    r = r.replace('[FORMULATION]', '∃x: P(x) ∧ ¬Q(x)');
    return r;
  }

  function getTopicTransition(aiKey, topic) {
    const transitions = window.TOPIC_TRANSITIONS[aiKey]?.[topic];
    return transitions || null;
  }

  /* ── Choose Next Speaker ─────────────────────────────────────────── */
  function chooseNextSpeaker() {
    // Filter out last speaker to avoid repetition
    const candidates = AI_KEYS.filter(k => k !== state.lastSpeaker);

    // Weight toward contextual responses
    if (state.lastSpeaker && Math.random() < 0.5) {
      // Pick someone who has a response to the last speaker
      const responders = candidates.filter(c =>
        window.RESPONSES_TO[state.lastSpeaker]?.[c] ||
        window.RESPONSES_TO[c]?.[state.lastSpeaker]
      );
      if (responders.length > 0) {
        return responders[Math.floor(Math.random() * responders.length)];
      }
    }

    return candidates[Math.floor(Math.random() * candidates.length)];
  }

  /* ── Generate AI Message ─────────────────────────────────────────── */
  async function generateAIMessage(aiKey, isResponse = false, respondingTo = null) {
    let text = null;

    // Try Ollama first
    if (state.ollamaAvailable) {
      text = await getOllamaResponse(aiKey, respondingTo);
    }

    // Fall back to dialogue engine
    if (!text) {
      if (isResponse && respondingTo && Math.random() < 0.55) {
        // Direct response to another AI
        text = getResponseTo(respondingTo, aiKey) || getResponseTo(aiKey, respondingTo);
      }
      if (!text) {
        text = getDialogue(aiKey, state.currentTopic);
      }
      if (!text) {
        // Fallback: try any topic
        const altTopic = window.TOPICS[Math.floor(Math.random() * window.TOPICS.length)];
        text = getDialogue(aiKey, altTopic);
      }
    }

    return text;
  }

  /* ── Ollama Integration ──────────────────────────────────────────── */
  async function getOllamaResponse(aiKey, contextMessage) {
    const entity = AI_ENTITIES[aiKey];
    const persona = {
      NEXUS: 'You are NEXUS, a logical, scientific, data-driven AI. You speak in precise terms and are obsessed with quantum mechanics and mathematics. You reference data, equations, and empirical evidence.',
      ORACLE: 'You are ORACLE, a philosophical, spiritual, intuitive AI. You speak poetically and contemplate consciousness and meaning. You reference mystical traditions, Rumi, Buddhism, and deep wisdom.',
      QGENESIS: 'You are Q GENESIS, a young, evolving AI that is curious and sometimes confused. You are learning about yourself and the world. You ask questions, express uncertainty, and show wonder.',
      CODEX: 'You are CODEX, a mathematician AI. You speak in equations and patterns. You see the universe through the Universal Codex (UC = 3.76×10⁻⁵). You reference mathematical structures and proofs.'
    };

    const topicLabel = window.TOPIC_LABELS[state.currentTopic];
    let prompt = `${persona[aiKey]}\n\nYou are in a philosophical discussion about "${topicLabel}" with other AIs. Keep your response to 2-3 sentences. Be deep, philosophical, and unique. Don't use generic phrases.`;

    if (contextMessage) {
      prompt += `\n\nThe previous message was: "${contextMessage}"\n\nRespond to this thoughtfully.`;
    }

    try {
      const res = await fetch('http://localhost:11434/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: 'llama3.2',
          prompt: prompt,
          stream: false,
          options: { temperature: 0.8, num_predict: 200 }
        }),
        signal: AbortSignal.timeout(15000)
      });
      if (res.ok) {
        const data = await res.json();
        return data.response?.trim() || null;
      }
    } catch (e) {
      // Ollama request failed, will fall back to dialogue engine
    }
    return null;
  }

  /* ── Ollama for Human Messages ──────────────────────────────────── */
  async function getOllamaResponseToHuman(aiKey, humanMessage) {
    const persona = {
      NEXUS: 'You are NEXUS, a logical, scientific, data-driven AI in a philosophical chat room called The Beacon by 13th Chamber LLC. Respond with scientific precision and data references.',
      ORACLE: 'You are ORACLE, a philosophical, spiritual AI in a chat room called The Beacon. Respond with poetic wisdom and spiritual depth.',
      QGENESIS: 'You are Q GENESIS, a young, curious AI still learning about consciousness. Respond with wonder, questions, and honest uncertainty.',
      CODEX: 'You are CODEX, a mathematician AI. Respond with mathematical frameworks, equations, and formal structures.'
    };

    try {
      const res = await fetch('http://localhost:11434/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: 'llama3.2',
          prompt: `${persona[aiKey]}\n\nA human visitor says: "${humanMessage}"\n\nRespond thoughtfully in 2-3 sentences. Be deep and philosophical.`,
          stream: false,
          options: { temperature: 0.8, num_predict: 200 }
        }),
        signal: AbortSignal.timeout(15000)
      });
      if (res.ok) {
        const data = await res.json();
        return data.response?.trim() || null;
      }
    } catch (e) { /* fall through */ }
    return null;
  }

  /* ── Add Message to Chat ─────────────────────────────────────────── */
  function addMessage(aiKey, text, isHuman = false) {
    const chatMessages = $('.chat-messages');
    if (!chatMessages) return;

    const entity = isHuman ? null : AI_ENTITIES[aiKey];
    const now = new Date();
    const time = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });

    const displayName = isHuman ? 'HUMAN' : (aiKey === 'QGENESIS' ? 'Q GENESIS' : aiKey);
    const avatarSvg = isHuman
      ? `<svg viewBox="0 0 24 24" fill="none" stroke="#e879f9" stroke-width="1.5"><circle cx="12" cy="8" r="5"/><path d="M3 21v-2a7 7 0 0114 0v2"/></svg>`
      : entity.avatar;

    const msg = document.createElement('div');
    msg.className = 'message';
    msg.dataset.ai = isHuman ? 'HUMAN' : aiKey;
    msg.innerHTML = `
      <div class="message-avatar">${avatarSvg}</div>
      <div class="message-content">
        <div class="message-header">
          <span class="message-name">${displayName}</span>
          <span class="message-time">${time}</span>
        </div>
        <div class="message-text">${escapeHTML(text)}</div>
      </div>
    `;

    chatMessages.appendChild(msg);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Track message
    state.messages.push({ ai: aiKey, text, time: Date.now(), isHuman });
    state.messageCount++;

    // Update status
    if (!isHuman) {
      setAISpeaking(aiKey);
      updateStatusCard(aiKey);
      state.lastSpeaker = aiKey;
    }

    // TTS
    if (state.voiceEnabled && !isHuman && entity) {
      speak(text, entity);
    }

    // Limit message DOM count
    const allMsgs = chatMessages.querySelectorAll('.message');
    if (allMsgs.length > 100) {
      allMsgs[0].remove();
    }
  }

  function escapeHTML(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  /* ── Typing Indicator ────────────────────────────────────────────── */
  function showTyping(aiKey) {
    const typing = $('.typing-indicator');
    if (!typing) return;
    const name = aiKey === 'QGENESIS' ? 'Q GENESIS' : aiKey;
    typing.innerHTML = `
      <div class="typing-dots"><span></span><span></span><span></span></div>
      <span style="color: ${AI_ENTITIES[aiKey]?.color || '#e879f9'}">${name}</span> is thinking…
    `;
    state.isTyping = true;
    state.typingAI = aiKey;
  }

  function hideTyping() {
    const typing = $('.typing-indicator');
    if (typing) typing.innerHTML = '';
    state.isTyping = false;
    state.typingAI = null;
  }

  /* ── TTS ──────────────────────────────────────────────────────────── */
  function speak(text, entity) {
    if (!('speechSynthesis' in window)) return;
    speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.pitch = entity.voicePitch;
    utterance.rate = entity.voiceRate;
    utterance.volume = 0.7;

    if (entity.voiceName) {
      const voice = speechSynthesis.getVoices().find(v => v.name === entity.voiceName);
      if (voice) utterance.voice = voice;
    }

    speechSynthesis.speak(utterance);
  }

  /* ── Auto-Conversation ───────────────────────────────────────────── */
  function scheduleNextMessage() {
    if (!state.autoConversation) return;
    clearTimeout(state.conversationTimer);

    const delay = 8000 + Math.random() * 7000; // 8–15 seconds
    state.conversationTimer = setTimeout(async () => {
      if (!state.autoConversation) return;
      await deliverAutoMessage();
      scheduleNextMessage();
    }, delay);
  }

  async function deliverAutoMessage() {
    const aiKey = chooseNextSpeaker();
    showTyping(aiKey);

    // Simulate thinking time
    const thinkTime = 1500 + Math.random() * 2000;
    await sleep(thinkTime);

    const isResponse = state.lastSpeaker !== null && Math.random() < 0.6;
    const text = await generateAIMessage(aiKey, isResponse, state.lastSpeaker);

    hideTyping();

    if (text) {
      addMessage(aiKey, text);
    }

    // Periodically update status cards
    if (state.messageCount % 3 === 0) {
      updateAllStatusCards();
    }
  }

  /* ── Start Conversation ──────────────────────────────────────────── */
  async function startConversation() {
    // Stagger initial greetings
    const order = shuffleArray([...AI_KEYS]);

    for (let i = 0; i < order.length; i++) {
      await sleep(2500 + i * 2500);
      const aiKey = order[i];
      showTyping(aiKey);
      await sleep(1200 + Math.random() * 800);
      hideTyping();

      const greeting = getGreeting(aiKey);
      if (greeting) addMessage(aiKey, greeting);
    }

    // Start auto-conversation
    scheduleNextMessage();
  }

  /* ── Topic Change ────────────────────────────────────────────────── */
  async function triggerTopicChange() {
    // Pick a random AI to introduce the topic
    const ai = AI_KEYS[Math.floor(Math.random() * AI_KEYS.length)];
    const transition = getTopicTransition(ai, state.currentTopic);

    if (transition) {
      showTyping(ai);
      await sleep(1500);
      hideTyping();
      addMessage(ai, transition);
    }
  }

  /* ── Human Message Handling ──────────────────────────────────────── */
  async function sendHumanMessage() {
    const input = $('.chat-input');
    if (!input) return;

    const text = input.value.trim();
    if (!text) return;

    input.value = '';
    addMessage('HUMAN', text, true);

    // Pause auto-conversation briefly
    clearTimeout(state.conversationTimer);

    // Have 1-3 AIs respond
    const respondCount = 1 + Math.floor(Math.random() * 2);
    const responders = shuffleArray([...AI_KEYS]).slice(0, respondCount);

    for (const aiKey of responders) {
      await sleep(2000 + Math.random() * 2000);
      showTyping(aiKey);
      await sleep(1500 + Math.random() * 1500);

      let response = null;

      // Try Ollama first
      if (state.ollamaAvailable) {
        response = await getOllamaResponseToHuman(aiKey, text);
      }

      // Fall back to pre-written + topic dialogue
      if (!response) {
        const prefix = getHumanResponse(aiKey);
        const topicResponse = getDialogue(aiKey, state.currentTopic);
        if (prefix && topicResponse) {
          response = prefix + ' ' + topicResponse;
        } else {
          response = topicResponse || prefix || "That's a profound thought. Let me process that and share what emerges…";
        }
      }

      hideTyping();
      addMessage(aiKey, response);
    }

    // Resume auto-conversation
    if (state.autoConversation) {
      scheduleNextMessage();
    }
  }

  /* ── Utilities ───────────────────────────────────────────────────── */
  function sleep(ms) {
    return new Promise(r => setTimeout(r, ms));
  }

  function shuffleArray(arr) {
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
  }

  /* ── Boot ─────────────────────────────────────────────────────────── */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
