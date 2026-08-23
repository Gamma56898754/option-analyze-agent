const chatMessages = document.getElementById(
    "chat-messages"
);

const chatForm = document.getElementById(
    "chat-form"
);

const messageInput = document.getElementById(
    "message-input"
);

const sendButton = document.getElementById(
    "send-button"
);

const newChatButton = document.getElementById(
    "new-chat-button"
);

const renameTitleButton = document.getElementById(
    "rename-title-button"
);

const conversationList = document.getElementById(
    "conversation-list"
);

const conversationTitle = document.getElementById(
    "conversation-title"
);

const statusText = document.getElementById(
    "status-text"
);

const THREAD_ID_STORAGE_KEY =
    "option_agent_thread_id";


function createThreadId() {
    return `web-${crypto.randomUUID()}`;
}


function getThreadId() {
    let threadId = localStorage.getItem(
        THREAD_ID_STORAGE_KEY
    );

    if (!threadId) {
        threadId = createThreadId();

        localStorage.setItem(
            THREAD_ID_STORAGE_KEY,
            threadId
        );
    }

    return threadId;
}


function setThreadId(threadId) {
    localStorage.setItem(
        THREAD_ID_STORAGE_KEY,
        threadId
    );
}


function scrollToBottom() {
    chatMessages.scrollTop =
        chatMessages.scrollHeight;
}


function clearMessages() {
    chatMessages.replaceChildren();
}


function addMessage(role, content) {
    const message = document.createElement(
        "article"
    );

    const roleLabel = document.createElement(
        "div"
    );

    const messageContent = document.createElement(
        "div"
    );

    message.classList.add("message");
    roleLabel.classList.add("message-role");
    messageContent.classList.add(
        "message-content"
    );

    if (role === "user") {
        message.classList.add("user-message");
        roleLabel.textContent = "你";
    } else if (role === "error") {
        message.classList.add("error-message");
        roleLabel.textContent = "系统错误";
    } else {
        message.classList.add("assistant-message");
        roleLabel.textContent = "Option Agent";
    }

    messageContent.textContent = content;

    message.append(roleLabel, messageContent);
    chatMessages.append(message);

    scrollToBottom();
}


function showWelcomeMessage() {
    addMessage(
        "assistant",
        "你好。你可以例如输入：\n" +
        "“分析 TSLA 2026-08-21 的 GEX”，\n" +
        "或在分析后继续问：“再详细解释一下”。"
    );
}


function setLoading(isLoading) {
    sendButton.disabled = isLoading;
    messageInput.disabled = isLoading;
    newChatButton.disabled = isLoading;
    renameTitleButton.disabled = isLoading;

    statusText.textContent = isLoading
        ? "Agent 正在分析，请稍候…"
        : "";
}


async function fetchJson(url, options = {}) {
    const response = await fetch(
        url,
        options
    );

    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data.detail || "请求执行失败。"
        );
    }

    return data;
}


async function loadConversations() {
    const conversations = await fetchJson(
        "/conversations"
    );

    conversationList.replaceChildren();

    if (conversations.length === 0) {
        const emptyText = document.createElement(
            "div"
        );

        emptyText.classList.add(
            "empty-conversations"
        );

        emptyText.textContent =
            "还没有已保存的会话。";

        conversationList.append(emptyText);

        return;
    }

    const currentThreadId = getThreadId();

    for (const conversation of conversations) {
        const item = document.createElement(
            "button"
        );

        const title = document.createElement(
            "div"
        );

        const time = document.createElement(
            "div"
        );

        item.type = "button";

        item.classList.add(
            "conversation-item"
        );

        if (
            conversation.thread_id ===
            currentThreadId
        ) {
            item.classList.add("active");
        }

        title.classList.add(
            "conversation-item-title"
        );

        time.classList.add(
            "conversation-item-time"
        );

        title.textContent = conversation.title;

        time.textContent = new Date(
            conversation.updated_at
        ).toLocaleString();

        item.append(title, time);

        item.addEventListener(
            "click",
            async () => {
                await openConversation(
                    conversation.thread_id,
                    conversation.title
                );
            }
        );

        conversationList.append(item);
    }
}


async function openConversation(
    threadId,
    title,
) {
    setThreadId(threadId);

    conversationTitle.textContent = title;

    const messages = await fetchJson(
        `/conversations/${threadId}/messages`
    );

    clearMessages();

    for (const message of messages) {
        addMessage(
            message.role,
            message.content
        );
    }

    requestAnimationFrame(
        scrollToBottom
    );

    await loadConversations();
}


async function sendMessage(message) {
    return fetchJson("/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            message: message,
            thread_id: getThreadId(),
        }),
    });
}


chatForm.addEventListener(
    "submit",
    async (event) => {
        event.preventDefault();

        const message = messageInput.value.trim();

        if (!message) {
            return;
        }

        addMessage("user", message);

        messageInput.value = "";
        setLoading(true);

        try {
            const result = await sendMessage(message);

            addMessage(
                "assistant",
                result.answer
            );

            await loadConversations();

            const conversations = await fetchJson(
                "/conversations"
            );

            const activeConversation =
                conversations.find(
                    (conversation) =>
                        conversation.thread_id ===
                        getThreadId()
                );

            if (activeConversation) {
                conversationTitle.textContent =
                    activeConversation.title;
            }
        } catch (error) {
            addMessage(
                "error",
                error.message ||
                "无法连接到 Agent 服务。"
            );
        } finally {
            setLoading(false);
            messageInput.focus();
        }
    }
);


newChatButton.addEventListener(
    "click",
    () => {
        setThreadId(createThreadId());

        conversationTitle.textContent = "新对话";

        clearMessages();
        showWelcomeMessage();

        loadConversations().catch(
            (error) => {
                console.error(error);
            }
        );

        messageInput.focus();
    }
);


renameTitleButton.addEventListener(
    "click",
    async () => {
        const currentTitle =
            conversationTitle.textContent;

        const title = window.prompt(
            "请输入新的会话标题：",
            currentTitle
        );

        if (!title || !title.trim()) {
            return;
        }

        try {
            const conversation = await fetchJson(
                `/conversations/${getThreadId()}`,
                {
                    method: "PATCH",
                    headers: {
                        "Content-Type":
                            "application/json",
                    },
                    body: JSON.stringify({
                        title: title.trim(),
                    }),
                }
            );

            conversationTitle.textContent =
                conversation.title;

            await loadConversations();
        } catch (error) {
            addMessage(
                "error",
                error.message ||
                "修改标题失败。"
            );
        }
    }
);


messageInput.addEventListener(
    "keydown",
    (event) => {
        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {
            event.preventDefault();
            chatForm.requestSubmit();
        }
    }
);


async function initializePage() {
    try {
        await loadConversations();

        const currentThreadId = getThreadId();

        const conversations = await fetchJson(
            "/conversations"
        );

        const currentConversation =
            conversations.find(
                (conversation) =>
                    conversation.thread_id ===
                    currentThreadId
            );

        if (currentConversation) {
            await openConversation(
                currentConversation.thread_id,
                currentConversation.title
            );
        } else {
            conversationTitle.textContent = "新对话";
            showWelcomeMessage();
        }
    } catch (error) {
        addMessage(
            "error",
            "无法加载会话记录。"
        );

        console.error(error);
    } finally {
        messageInput.focus();
    }
}


initializePage();