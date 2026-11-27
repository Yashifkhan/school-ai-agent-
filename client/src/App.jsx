import { useCallback, useEffect, useRef, useState } from 'react'
import './App.css'

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '')
const CHAT_ENDPOINT = `${API_BASE_URL}/api/chat`
const HEALTH_ENDPOINT = `${API_BASE_URL}/health`

const prompts = [
  {
    icon: 'book',
    title: 'Add a new student',
    description: 'Learn the student registration workflow',
    query: 'How do I add a new student?',
  },
  {
    icon: 'route',
    title: 'Manage school transport',
    description: 'Explore routes, vehicles, and assignments',
    query: 'How do I manage student transport?',
  },
  {
    icon: 'calendar',
    title: 'Understand attendance',
    description: 'Get help with attendance workflows',
    query: 'How does student attendance tracking work?',
  },
  {
    icon: 'sparkles',
    title: 'Ask a general question',
    description: 'Get a clear answer from your AI assistant',
    query: 'What are some practical ways to improve parent engagement?',
  },
]

function Icon({ name, size = 18, className = '' }) {
  const sharedProps = {
    'aria-hidden': true,
    className,
    fill: 'none',
    height: size,
    stroke: 'currentColor',
    strokeLinecap: 'round',
    strokeLinejoin: 'round',
    strokeWidth: 1.8,
    viewBox: '0 0 24 24',
    width: size,
  }

  const paths = {
    arrow: <><path d="M12 19V5" /><path d="m6 11 6-6 6 6" /></>,
    book: <><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v17H6.5A2.5 2.5 0 0 1 4 17.5z" /><path d="M4 17.5A2.5 2.5 0 0 1 6.5 15H20" /><path d="M8 7h8M8 10h6" /></>,
    calendar: <><rect height="17" rx="2.5" width="18" x="3" y="4" /><path d="M16 2v4M8 2v4M3 10h18" /><path d="m9 15 2 2 4-4" /></>,
    check: <><path d="m5 12 4 4L19 6" /></>,
    close: <><path d="m18 6-12 12M6 6l12 12" /></>,
    menu: <><path d="M4 7h16M4 12h16M4 17h16" /></>,
    plus: <><path d="M12 5v14M5 12h14" /></>,
    route: <><circle cx="6" cy="6" r="2.5" /><circle cx="18" cy="18" r="2.5" /><path d="M8.5 6H14a4 4 0 0 1 0 8h-4a4 4 0 0 0 0 8h5.5" /></>,
    send: <><path d="m21 3-7.5 18-3.8-7.7L2 9.5 21 3Z" /><path d="M9.7 13.3 14 9" /></>,
    sparkles: <><path d="m12 3 1.9 5.8L20 11l-6.1 2.2L12 19l-1.9-5.8L4 11l6.1-2.2L12 3Z" /><path d="m19 14 1.1 2.9L23 18l-2.9 1.1L19 22l-1.1-2.9L15 18l2.9-1.1L19 14Z" /></>,
    retry: <><path d="M20 7v5h-5" /><path d="M4.9 9A7.5 7.5 0 0 1 18 6l2 6" /><path d="M4 17v-5h5" /><path d="M19.1 15A7.5 7.5 0 0 1 6 18l-2-6" /></>,
  }

  return <svg {...sharedProps}>{paths[name] ?? paths.sparkles}</svg>
}

function createMessageId() {
  return globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`
}

function getModelSelection(catalog, currentSelection = {}) {
  const providers = Array.isArray(catalog.providers) ? catalog.providers : []
  const provider = providers.find(
    (item) => item.id === currentSelection.provider && item.configured,
  ) ?? providers.find((item) => item.id === catalog.default_provider)
    ?? providers.find((item) => item.configured)
    ?? providers[0]

  if (!provider) return { provider: '', model: '' }

  const selectedModel = provider.models.find(
    (item) => item.id === currentSelection.model && item.selectable !== false,
  )

  return {
    provider: provider.id,
    model: selectedModel?.id
      ?? provider.default_model
      ?? provider.models.find((item) => item.selectable !== false)?.id
      ?? '',
  }
}

function App() {
  const [messages, setMessages] = useState([])
  const [draft, setDraft] = useState('')
  const [isSending, setIsSending] = useState(false)
  const [apiStatus, setApiStatus] = useState('checking')
  const [modelProviders, setModelProviders] = useState([])
  const [modelSelection, setModelSelection] = useState({ provider: 'gemini', model: '' })
  const [modelCatalogLoaded, setModelCatalogLoaded] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const textareaRef = useRef(null)
  const chatAreaRef = useRef(null)
  const shouldAutoScrollRef = useRef(true)
  const activeRequestRef = useRef(null)

  const checkApi = useCallback(async () => {
    const response = await fetch(HEALTH_ENDPOINT, {
      signal: AbortSignal.timeout(8000),
    })
    if (!response.ok) throw new Error('Unable to load AI options.')

    const catalog = await response.json()
    if (!Array.isArray(catalog.providers)) {
      throw new Error('The API did not return available AI providers.')
    }

    return catalog
  }, [])

  useEffect(() => {
    let active = true
    checkApi()
      .then((catalog) => {
        if (!active) return
        setModelProviders(catalog.providers)
        setModelSelection(getModelSelection(catalog))
        setModelCatalogLoaded(true)
        setApiStatus('online')
      })
      .catch(() => {
        if (!active) return
        setModelCatalogLoaded(true)
        setApiStatus('offline')
      })

    return () => {
      active = false
    }
  }, [checkApi])

  useEffect(() => {
    const chatArea = chatAreaRef.current
    if (!chatArea || !messages.length || !shouldAutoScrollRef.current) return

    chatArea.scrollTo({
      top: chatArea.scrollHeight,
      behavior: 'smooth',
    })
  }, [messages])

  useEffect(() => {
    const textarea = textareaRef.current
    if (!textarea) return

    textarea.style.height = 'auto'
    textarea.style.height = `${Math.min(textarea.scrollHeight, 144)}px`
  }, [draft])

  useEffect(() => () => activeRequestRef.current?.abort(), [])

  const selectedProvider = modelProviders.find(
    (provider) => provider.id === modelSelection.provider,
  )
  const selectedModels = selectedProvider?.models ?? []
  const selectionReady = Boolean(
    modelCatalogLoaded
    && selectedProvider?.configured
    && selectedModels.some(
      (item) => item.id === modelSelection.model && item.selectable !== false,
    ),
  )

  const runAgent = useCallback(async (query, assistantId, selection) => {
    const controller = new AbortController()
    activeRequestRef.current = controller
    setIsSending(true)
    setMessages((current) => current.map((message) => (
      message.id === assistantId
        ? { ...message, content: '', status: 'loading' }
        : message
    )))

    const timeout = setTimeout(() => controller.abort(), 90000)

    try {
      const response = await fetch(CHAT_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query,
          provider: selection.provider,
          model: selection.model,
        }),
        signal: controller.signal,
      })
      const result = await response.json().catch(() => ({}))
      if (!response.ok) {
        throw new Error(result.detail || `The request failed (${response.status}).`)
      }
      if (typeof result.answer !== 'string' || !result.answer.trim()) {
        throw new Error('The assistant returned an empty response. Please try again.')
      }

      setMessages((current) => current.map((message) => (
        message.id === assistantId
          ? { ...message, content: result.answer, status: 'complete' }
          : message
      )))
    } catch (error) {
      const content = controller.signal.aborted
        ? 'This request took too long or was cancelled. Please try again.'
        : error instanceof TypeError
          ? 'Could not connect to the AI service. Check that the backend is running, then try again.'
          : error.message || 'Something went wrong. Please try again.'

      setMessages((current) => current.map((message) => (
        message.id === assistantId
          ? { ...message, content, status: 'error' }
          : message
      )))
    } finally {
      clearTimeout(timeout)
      if (activeRequestRef.current === controller) {
        activeRequestRef.current = null
        setIsSending(false)
      }
    }
  }, [])

  const sendMessage = useCallback((value = draft) => {
    const query = value.trim()
    if (!query || isSending || !selectionReady) return

    const assistantId = createMessageId()
    const selectedAI = { ...modelSelection }
    shouldAutoScrollRef.current = true
    setMessages((current) => [
      ...current,
      {
        id: createMessageId(),
        role: 'user',
        content: query,
        provider: selectedAI.provider,
        model: selectedAI.model,
      },
      {
        id: assistantId,
        role: 'assistant',
        content: '',
        status: 'loading',
        query,
        provider: selectedAI.provider,
        model: selectedAI.model,
      },
    ])
    setDraft('')
    setSidebarOpen(false)
    runAgent(query, assistantId, selectedAI)
  }, [draft, isSending, modelSelection, runAgent, selectionReady])

  const startNewChat = () => {
    activeRequestRef.current?.abort()
    activeRequestRef.current = null
    setIsSending(false)
    setMessages([])
    shouldAutoScrollRef.current = true
    setDraft('')
    setSidebarOpen(false)
    textareaRef.current?.focus()
  }

  const handleChatAreaScroll = () => {
    const chatArea = chatAreaRef.current
    if (!chatArea) return

    const distanceFromBottom = (
      chatArea.scrollHeight - chatArea.scrollTop - chatArea.clientHeight
    )
    shouldAutoScrollRef.current = distanceFromBottom < 96
  }

  const refreshApiStatus = async () => {
    setApiStatus('checking')
    try {
      const catalog = await checkApi()
      setModelProviders(catalog.providers)
      setModelSelection((current) => getModelSelection(catalog, current))
      setModelCatalogLoaded(true)
      setApiStatus('online')
    } catch {
      setModelCatalogLoaded(true)
      setApiStatus('offline')
    }
  }

  const handleProviderChange = (event) => {
    const provider = modelProviders.find((item) => item.id === event.target.value)
    if (!provider) return

    setModelSelection({
      provider: provider.id,
      model: provider.default_model ?? provider.models[0]?.id ?? '',
    })
  }

  const handleModelChange = (event) => {
    if (!selectedModels.some(
      (item) => item.id === event.target.value && item.selectable !== false,
    )) return

    setModelSelection((current) => ({ ...current, model: event.target.value }))
  }

  const handleSubmit = (event) => {
    event.preventDefault()
    sendMessage()
  }

  const handleKeyDown = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      sendMessage()
    }
  }

  const statusLabel = {
    checking: 'Checking API',
    online: 'API connected',
    offline: 'API offline',
  }[apiStatus]

  return (
    <div className="app-shell">
      {sidebarOpen && (
        <button
          className="sidebar-backdrop"
          aria-label="Close navigation"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <aside className={`sidebar ${sidebarOpen ? 'sidebar-open' : ''}`}>
        <div className="sidebar-scroll">
          <div className="brand">
            <div className="brand-mark"><Icon name="sparkles" size={20} /></div>
            <div className="brand-copy">
              <span className="brand-name">aster</span>
              <span className="brand-caption">SCHOOL INTELLIGENCE</span>
            </div>
            <button
              className="icon-button sidebar-close"
              aria-label="Close navigation"
              onClick={() => setSidebarOpen(false)}
            >
              <Icon name="close" />
            </button>
          </div>

          <div className="workspace-label">WORKSPACE</div>
          <div className="workspace-card">
            <div className="workspace-avatar">S</div>
            <div className="workspace-copy">
              <strong>School workspace</strong>
              <span>AI operations assistant</span>
            </div>
            <span className="workspace-indicator" aria-hidden="true" />
          </div>

          <div className="sidebar-section-label">YOUR SPACE</div>
          <div className="nav-item nav-item-active" aria-current="page">
            <Icon name="sparkles" size={17} />
            <span>AI assistant</span>
          </div>
          <button className="nav-item nav-new-chat" onClick={startNewChat}>
            <Icon name="plus" size={17} />
            <span>New conversation</span>
          </button>

          <div className="sidebar-divider" />
          <div className="sidebar-section-label flow-label">AGENT FLOW</div>
          <div className="flow-list">
            <div className="flow-step">
              <span className="flow-step-icon"><Icon name="sparkles" size={14} /></span>
              <span>Understand intent</span>
            </div>
            <div className="flow-connector" />
            <div className="flow-step">
              <span className="flow-step-icon"><Icon name="route" size={14} /></span>
              <span>Choose relevant sources</span>
            </div>
            <div className="flow-connector" />
            <div className="flow-step">
              <span className="flow-step-icon"><Icon name="book" size={14} /></span>
              <span>Ground the response</span>
            </div>
          </div>

        </div>
        <div className="sidebar-footer">
          <div className={`connection-dot connection-${apiStatus}`} />
          <span>{statusLabel}</span>
          <button
            className="refresh-status"
            onClick={refreshApiStatus}
            aria-label="Check API connection"
            title="Check API connection"
          >
            <Icon name="retry" size={14} />
          </button>
        </div>
      </aside>

      <main className="main-panel">
        <header className="topbar">
          <div className="topbar-left">
            <button
              className="icon-button mobile-menu"
              aria-label="Open navigation"
              onClick={() => setSidebarOpen(true)}
            >
              <Icon name="menu" />
            </button>
            <div className="breadcrumb">
              <span>Workspace</span>
              <span className="breadcrumb-divider">/</span>
              <strong>AI assistant</strong>
            </div>
          </div>
          <div className="topbar-actions">
            <div
              className={`status-pill status-${apiStatus}`}
              role="status"
              aria-label={statusLabel}
            >
              <span className="status-dot" />
              <span>{statusLabel}</span>
            </div>
            <button
              className="new-chat-button"
              onClick={startNewChat}
              aria-label="Start a new chat"
            >
              <Icon name="plus" size={16} />
              <span>New chat</span>
            </button>
          </div>
        </header>

        <section
          ref={chatAreaRef}
          className={`chat-area ${messages.length ? 'chat-area-active' : ''}`}
          onScroll={handleChatAreaScroll}
        >
          {messages.length === 0 ? (
            <div className="welcome-screen">
              <div className="welcome-orb" aria-hidden="true">
                <div className="orb-ring orb-ring-outer" />
                <div className="orb-ring orb-ring-inner" />
                <div className="orb-core"><Icon name="sparkles" size={28} /></div>
                <span className="orb-star orb-star-one">✦</span>
                <span className="orb-star orb-star-two">✧</span>
              </div>
              <div className="welcome-eyebrow">
                <span className="eyebrow-line" />
                YOUR SCHOOL AI ASSISTANT
                <span className="eyebrow-line" />
              </div>
              <h1>School operations,<br /><span>in better flow.</span></h1>
              <p className="welcome-description">
                Ask a question in plain language. Your AI agent finds the right
                path and gives you a clear, grounded answer.
              </p>

              <div className="suggestion-grid">
                {prompts.map((prompt, index) => (
                  <button
                    className="suggestion-card"
                    key={prompt.title}
                    onClick={() => sendMessage(prompt.query)}
                    disabled={isSending || !selectionReady}
                    style={{ '--card-index': index }}
                  >
                    <span className="suggestion-icon"><Icon name={prompt.icon} size={17} /></span>
                    <span className="suggestion-content">
                      <strong>{prompt.title}</strong>
                      <span>{prompt.description}</span>
                    </span>
                    <span className="suggestion-arrow">↗</span>
                  </button>
                ))}
              </div>

              <div className="privacy-note">
                <Icon name="check" size={14} />
                <span>The agent only answers with information available to it.</span>
              </div>
            </div>
          ) : (
            <div className="conversation" aria-live="polite">
              {messages.map((message) => (
                <article className={`message message-${message.role}`} key={message.id}>
                  {message.role === 'assistant' && (
                    <div className="assistant-avatar"><Icon name="sparkles" size={16} /></div>
                  )}
                  <div className="message-body">
                    <div className="message-meta">
                      <strong>{message.role === 'assistant' ? 'Aster' : 'You'}</strong>
                      {message.role === 'assistant' && message.status === 'complete' && (
                        <span className="answer-label"><Icon name="check" size={12} /> Grounded answer</span>
                      )}
                    </div>
                    {message.status === 'loading' ? (
                      <div className="thinking-card">
                        <span className="thinking-indicator"><i /><i /><i /></span>
                        <span>Thinking through your question…</span>
                      </div>
                    ) : (
                      <div
                        className={`message-content ${message.role === 'user' ? 'user-content' : ''}`}
                        role={message.status === 'error' ? 'alert' : undefined}
                      >
                        {message.content}
                      </div>
                    )}
                    {message.status === 'error' && (
                      <button
                        className="retry-button"
                        disabled={isSending}
                        onClick={() => runAgent(message.query, message.id, {
                          provider: message.provider ?? modelSelection.provider,
                          model: message.model ?? modelSelection.model,
                        })}
                      >
                        <Icon name="retry" size={14} />
                        Try again
                      </button>
                    )}
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>

        <div className="composer-wrap">
          <form className="composer" onSubmit={handleSubmit}>
            <textarea
              ref={textareaRef}
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask anything about your school…"
              aria-label="Ask the AI assistant"
              maxLength={2000}
              rows={1}
              disabled={isSending}
            />
            <div className="composer-bottom">
              <div className="model-selectors">
                <label className="model-selector">
                  <span className="model-selector-label">AI</span>
                  <select
                    aria-label="AI provider"
                    value={modelSelection.provider}
                    onChange={handleProviderChange}
                    disabled={!modelCatalogLoaded || isSending}
                  >
                    {modelProviders.map((provider) => (
                      <option
                        key={provider.id}
                        value={provider.id}
                        disabled={!provider.configured}
                      >
                        {provider.name}{provider.configured ? '' : ' · key required'}
                      </option>
                    ))}
                    {!modelProviders.length && (
                      <option value="gemini">Load providers</option>
                    )}
                  </select>
                </label>
                <label className="model-selector model-selector-model">
                  <span className="model-selector-label">Model</span>
                  <select
                    aria-label="AI model"
                    value={modelSelection.model}
                    onChange={handleModelChange}
                    disabled={!selectionReady || isSending}
                  >
                    {selectedModels.map((item) => (
                      <option
                        key={item.id}
                        value={item.id}
                        disabled={item.selectable === false}
                      >
                        {item.name}{item.reason ? ` · ${item.reason}` : ''}
                      </option>
                    ))}
                    {!selectedModels.length && (
                      <option value="">No models available</option>
                    )}
                  </select>
                </label>
              </div>
              <span className="composer-hint">
                <kbd>↵</kbd> to send <span className="hint-separator">·</span> <kbd>⇧ ↵</kbd> for a new line
              </span>
              <div className="composer-actions">
                <span className="character-count">{draft.length}/2000</span>
                <button
                  type="submit"
                  className={`send-button ${draft.trim() && !isSending && selectionReady ? 'send-ready' : ''}`}
                  disabled={!draft.trim() || isSending || !selectionReady}
                  aria-label="Send message"
                >
                  {isSending ? <span className="button-spinner" /> : <Icon name="send" size={17} />}
                </button>
              </div>
            </div>
          </form>
          <p className="composer-disclaimer">
            AI can make mistakes. Verify important school information.
          </p>
        </div>
      </main>
    </div>
  )
}

export default App
