interface ApiError {
    error?: string;
}

interface LikeResponse {
    liked: boolean;
    count: number;
}

interface CommentResponse {
    html?: string;
    count?: number;
    error?: string;
}

interface HtmlResponse {
    html: string;
}

interface ChatMessage {
    sender: string;
    message: string;
    created: string;
}

interface EarlierMessagesResponse {
    html: string;
    has_more: boolean;
    earliest_id: number | null;
}

interface NotificationEvent {
    unread_count: number;
    kind: string;
    actor: string;
}

function getCookie(name: string): string | null {
    const prefix = `${name}=`;
    const cookie = document.cookie
        .split(";")
        .map((part) => part.trim())
        .find((part) => part.startsWith(prefix));

    if (!cookie) return null;

    try {
        return decodeURIComponent(cookie.slice(prefix.length));
    } catch {
        return cookie.slice(prefix.length);
    }
}

async function requestJson<T>(url: string, options: RequestInit = {}): Promise<T> {
    const headers = new Headers(options.headers);
    if (options.method?.toUpperCase() === "POST") {
        const csrfToken = getCookie("csrftoken");
        if (csrfToken) headers.set("X-CSRFToken", csrfToken);
    }

    const response = await fetch(url, { ...options, headers });
    let payload: unknown;

    try {
        payload = await response.json();
    } catch {
        payload = {};
    }

    if (!response.ok) {
        const errorPayload = payload as ApiError;
        throw new Error(errorPayload.error || `Request failed (${response.status})`);
    }

    return payload as T;
}

function showToast(message: string, kind: "success" | "error" | "info" = "info"): void {
    const region = document.getElementById("toast-region");
    if (!region) return;

    const toast = document.createElement("div");
    toast.className = `toast toast--${kind}`;
    toast.setAttribute("role", kind === "error" ? "alert" : "status");
    toast.textContent = message;
    region.appendChild(toast);

    window.setTimeout(() => {
        toast.classList.add("toast--leaving");
        toast.addEventListener("transitionend", () => toast.remove(), { once: true });
        window.setTimeout(() => toast.remove(), 300);
    }, 3200);
}

function initializeNavigation(): void {
    const toggle = document.getElementById("navbar-toggle");
    const menu = document.getElementById("navbar-menu");
    if (!(toggle instanceof HTMLButtonElement) || !menu) return;

    const closeMenu = (): void => {
        menu.classList.remove("open");
        toggle.classList.remove("active");
        toggle.setAttribute("aria-expanded", "false");
    };

    toggle.addEventListener("click", () => {
        const isOpen = menu.classList.toggle("open");
        toggle.classList.toggle("active", isOpen);
        toggle.setAttribute("aria-expanded", String(isOpen));
    });

    menu.querySelectorAll("a, button").forEach((element) => {
        element.addEventListener("click", closeMenu);
    });
}

function initializeVideoLikes(): void {
    document.addEventListener("click", async (event) => {
        if (!(event.target instanceof Element)) return;
        const button = event.target.closest<HTMLButtonElement>(".video-like-btn");
        if (!button || !button.dataset.url || button.disabled) return;

        button.disabled = true;
        button.setAttribute("aria-busy", "true");

        try {
            const data = await requestJson<LikeResponse>(button.dataset.url, {
                method: "POST",
            });
            button.classList.toggle("liked", data.liked);
            button.setAttribute("aria-pressed", String(data.liked));
            button.textContent = data.liked ? "♥ Unlike" : "♡ Like";

            const count = document.getElementById(button.dataset.countTarget || "");
            if (count) {
                count.textContent = `${data.count} like${data.count === 1 ? "" : "s"}`;
            }
            showToast(data.liked ? "Added to your likes" : "Like removed", "success");
        } catch (error) {
            showToast(error instanceof Error ? error.message : "Could not update like", "error");
        } finally {
            button.disabled = false;
            button.removeAttribute("aria-busy");
        }
    });
}

function initializeComments(): void {
    const section = document.querySelector<HTMLElement>(".comment-section");
    if (!section) return;

    const form = document.getElementById("comment-form");
    const list = document.getElementById("comment-list");
    const count = document.getElementById("comment-count");
    if (!list || !count) return;

    if (form instanceof HTMLFormElement) {
        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            const textarea = form.querySelector<HTMLTextAreaElement>("textarea");
            const submit = form.querySelector<HTMLButtonElement>("button[type=submit]");
            if (!textarea || !submit || !textarea.value.trim()) return;

            submit.disabled = true;
            submit.setAttribute("aria-busy", "true");
            try {
                const data = await requestJson<CommentResponse>(section.dataset.addUrl || "", {
                    method: "POST",
                    body: new FormData(form),
                });
                if (!data.html || data.count === undefined) {
                    throw new Error(data.error || "Could not post comment");
                }

                list.querySelector(".comment-empty")?.remove();
                list.insertAdjacentHTML("afterbegin", data.html);
                count.textContent = `(${data.count})`;
                textarea.value = "";
                showToast("Comment posted", "success");
            } catch (error) {
                showToast(error instanceof Error ? error.message : "Could not post comment", "error");
            } finally {
                submit.disabled = false;
                submit.removeAttribute("aria-busy");
            }
        });
    }

    list.addEventListener("click", async (event) => {
        if (!(event.target instanceof Element)) return;
        const button = event.target.closest<HTMLButtonElement>(".comment-delete-btn");
        if (!button || !button.dataset.url || !button.dataset.commentId) return;
        if (!window.confirm("Delete this comment?")) return;

        button.disabled = true;
        try {
            const data = await requestJson<CommentResponse>(button.dataset.url, {
                method: "POST",
            });
            if (data.error || data.count === undefined) {
                throw new Error(data.error || "Could not delete comment");
            }

            document.getElementById(`comment-${button.dataset.commentId}`)?.remove();
            count.textContent = `(${data.count})`;
            if (list.children.length === 0) {
                list.innerHTML = '<p class="comment-empty">No comments yet. Be the first to say something.</p>';
            }
            showToast("Comment deleted", "success");
        } catch (error) {
            button.disabled = false;
            showToast(error instanceof Error ? error.message : "Could not delete comment", "error");
        }
    });
}

function websocketUrl(path: string): string {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    return `${protocol}//${window.location.host}${path}`;
}

function appendChatMessage(container: HTMLElement, data: ChatMessage, currentUsername: string): void {
    const message = document.createElement("div");
    message.className = `chat-message${data.sender === currentUsername ? " mine" : ""}`;

    const author = document.createElement("span");
    author.className = "chat-message-author";
    author.textContent = data.sender;

    const content = document.createElement("p");
    content.className = "chat-message-content";
    content.textContent = data.message;

    const time = document.createElement("span");
    time.className = "chat-message-time";
    time.textContent = data.created;

    message.append(author, content, time);
    container.appendChild(message);
    container.scrollTop = container.scrollHeight;
}

function initializeConversationDetail(): void {
    const page = document.querySelector<HTMLElement>(".chat-page");
    if (!page) return;

    const conversationId = page.dataset.conversationId;
    const currentUsername = page.dataset.currentUsername || "";
    const messages = document.getElementById("chat-messages");
    const form = document.getElementById("chat-form");
    const input = document.getElementById("chat-input");
    const status = document.getElementById("chat-status");
    if (!conversationId || !messages || !(form instanceof HTMLFormElement)
        || !(input instanceof HTMLInputElement)) return;

    let socket: WebSocket;
    try {
        socket = new WebSocket(websocketUrl(`/ws/chat/${conversationId}/`));
    } catch {
        if (status) status.textContent = "Chat connection unavailable";
        return;
    }

    socket.addEventListener("open", () => {
        if (status) status.textContent = "Connected";
    });
    socket.addEventListener("message", (event) => {
        try {
            appendChatMessage(messages, JSON.parse(String(event.data)) as ChatMessage, currentUsername);
        } catch {
            showToast("Received an unreadable chat message", "error");
        }
    });
    socket.addEventListener("close", () => {
        if (status) status.textContent = "Disconnected. Refresh to reconnect.";
    });
    socket.addEventListener("error", () => {
        if (status) status.textContent = "Chat connection error";
    });

    form.addEventListener("submit", (event) => {
        event.preventDefault();
        const text = input.value.trim();
        if (!text) return;
        if (socket.readyState !== WebSocket.OPEN) {
            showToast("Chat is reconnecting; your message was not sent", "error");
            return;
        }

        socket.send(JSON.stringify({ message: text }));
        input.value = "";
    });

    const earlierButton = document.getElementById("load-earlier-btn");
    earlierButton?.addEventListener("click", async () => {
        if (!(earlierButton instanceof HTMLButtonElement)) return;
        const url = earlierButton.dataset.url;
        const beforeId = earlierButton.dataset.beforeId;
        if (!url || !beforeId) return;

        earlierButton.disabled = true;
        const oldHeight = messages.scrollHeight;
        try {
            const separator = url.endsWith("/") ? "?" : "&";
            const data = await requestJson<EarlierMessagesResponse>(
                `${url}${separator}before=${encodeURIComponent(beforeId)}`,
            );
            messages.insertAdjacentHTML("afterbegin", data.html);
            messages.scrollTop += messages.scrollHeight - oldHeight;
            if (data.earliest_id !== null) {
                earlierButton.dataset.beforeId = String(data.earliest_id);
            }
            if (!data.has_more) earlierButton.remove();
        } catch (error) {
            showToast(error instanceof Error ? error.message : "Could not load earlier messages", "error");
            earlierButton.disabled = false;
        }
    });

    messages.scrollTop = messages.scrollHeight;
    window.addEventListener("pagehide", () => socket.close(), { once: true });
}

function initializePanels(): void {
    const nav = document.querySelector<HTMLElement>(".navbar");
    const overlay = document.getElementById("panel-overlay");
    const notificationPanel = document.getElementById("notif-panel");
    const messagePanel = document.getElementById("msg-panel");
    const notificationToggle = document.getElementById("notif-toggle");
    const messageToggle = document.getElementById("msg-toggle");
    const notificationBody = document.getElementById("notif-panel-body");
    const messageList = document.getElementById("msg-panel-list");
    const messageChat = document.getElementById("msg-panel-chat");
    const messageBack = document.getElementById("msg-panel-back");
    const messageTitle = document.getElementById("msg-panel-title");
    const chatMessages = document.getElementById("panel-chat-messages");
    const chatForm = document.getElementById("panel-chat-form");
    const chatInput = document.getElementById("panel-chat-input");
    const chatStatus = document.getElementById("panel-chat-status");
    const badge = document.getElementById("notif-badge");

    if (!nav || !overlay || !notificationPanel || !messagePanel
        || !(notificationToggle instanceof HTMLButtonElement)
        || !(messageToggle instanceof HTMLButtonElement)
        || !notificationBody || !messageList || !messageChat || !messageBack
        || !messageTitle || !chatMessages || !(chatForm instanceof HTMLFormElement)
        || !(chatInput instanceof HTMLInputElement)) return;

    let activeSocket: WebSocket | null = null;
    let previousTrigger: HTMLElement | null = null;

    const closePanels = (restoreFocus = false): void => {
        notificationPanel.classList.remove("open");
        messagePanel.classList.remove("open");
        notificationPanel.setAttribute("aria-hidden", "true");
        messagePanel.setAttribute("aria-hidden", "true");
        notificationToggle.setAttribute("aria-expanded", "false");
        messageToggle.setAttribute("aria-expanded", "false");
        overlay.classList.remove("visible");
        if (activeSocket) {
            activeSocket.close();
            activeSocket = null;
        }
        if (restoreFocus) previousTrigger?.focus();
    };

    const openPanel = (panel: HTMLElement, trigger: HTMLButtonElement): void => {
        closePanels();
        previousTrigger = trigger;
        panel.classList.add("open");
        panel.setAttribute("aria-hidden", "false");
        trigger.setAttribute("aria-expanded", "true");
        overlay.classList.add("visible");
    };

    overlay.addEventListener("click", () => closePanels(true));
    document.querySelectorAll<HTMLElement>("[data-close-panel]").forEach((button) => {
        button.addEventListener("click", () => closePanels(true));
    });
    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") closePanels(true);
    });

    notificationToggle.addEventListener("click", async () => {
        openPanel(notificationPanel, notificationToggle);
        try {
            const data = await requestJson<HtmlResponse>(nav.dataset.notificationsUrl || "");
            notificationBody.innerHTML = data.html;
            if (badge) badge.style.display = "none";
        } catch (error) {
            notificationBody.innerHTML = '<p class="panel-empty">Could not load notifications.</p>';
            showToast(error instanceof Error ? error.message : "Could not load notifications", "error");
        }
    });

    let notificationSocket: WebSocket | null = null;
    try {
        notificationSocket = new WebSocket(websocketUrl("/ws/notifications/"));
        notificationSocket.addEventListener("message", (event) => {
            try {
                const data = JSON.parse(String(event.data)) as NotificationEvent;
                if (badge) {
                    badge.textContent = String(data.unread_count);
                    badge.style.display = data.unread_count > 0 ? "flex" : "none";
                }
                const descriptions: Record<string, string> = {
                    follow: "started following you",
                    like: "liked your video",
                    comment: "commented on your post",
                    message: "sent you a message",
                };
                showToast(`${data.actor} ${descriptions[data.kind] || "sent you an update"}`, "info");
            } catch {
                showToast("Received an unreadable notification", "error");
            }
        });
    } catch {
        showToast("Live notifications are unavailable", "error");
    }

    const showMessageList = (): void => {
        messageList.style.display = "block";
        messageChat.style.display = "none";
        messageBack.style.display = "none";
        messageTitle.textContent = "Messages";
        if (activeSocket) {
            activeSocket.close();
            activeSocket = null;
        }
    };

    const openConversation = async (id: string, displayName: string): Promise<void> => {
        messageList.style.display = "none";
        messageChat.style.display = "flex";
        messageBack.style.display = "inline";
        messageTitle.textContent = displayName;
        chatStatus && (chatStatus.textContent = "Loading messages…");

        const messageUrl = nav.dataset.panelMessagesUrl?.replace("/0/messages/", `/${id}/messages/`);
        if (!messageUrl) return;
        try {
            const data = await requestJson<HtmlResponse>(messageUrl);
            chatMessages.innerHTML = data.html;
            chatMessages.scrollTop = chatMessages.scrollHeight;
        } catch (error) {
            chatMessages.innerHTML = '<p class="panel-empty">Could not load messages.</p>';
            showToast(error instanceof Error ? error.message : "Could not load messages", "error");
        }

        activeSocket?.close();
        activeSocket = new WebSocket(websocketUrl(`/ws/chat/${id}/`));
        activeSocket.addEventListener("open", () => {
            if (chatStatus) chatStatus.textContent = "Connected";
        });
        activeSocket.addEventListener("close", () => {
            if (chatStatus) chatStatus.textContent = "Disconnected";
        });
        activeSocket.addEventListener("message", (event) => {
            try {
                appendChatMessage(
                    chatMessages,
                    JSON.parse(String(event.data)) as ChatMessage,
                    nav.dataset.currentUsername || "",
                );
            } catch {
                showToast("Received an unreadable chat message", "error");
            }
        });
    };

    messageToggle.addEventListener("click", async () => {
        openPanel(messagePanel, messageToggle);
        showMessageList();
        try {
            const data = await requestJson<HtmlResponse>(nav.dataset.conversationsUrl || "");
            messageList.innerHTML = data.html;
            messageList.querySelectorAll<HTMLButtonElement>(".panel-conversation-item").forEach((button) => {
                button.addEventListener("click", () => {
                    const id = button.dataset.conversationId;
                    if (id) void openConversation(id, button.dataset.displayName || "Conversation");
                });
            });
        } catch (error) {
            messageList.innerHTML = '<p class="panel-empty">Could not load conversations.</p>';
            showToast(error instanceof Error ? error.message : "Could not load conversations", "error");
        }
    });

    messageBack.addEventListener("click", showMessageList);
    chatForm.addEventListener("submit", (event) => {
        event.preventDefault();
        const text = chatInput.value.trim();
        if (!text) return;
        if (!activeSocket || activeSocket.readyState !== WebSocket.OPEN) {
            showToast("Chat is reconnecting; your message was not sent", "error");
            return;
        }
        activeSocket.send(JSON.stringify({ message: text }));
        chatInput.value = "";
    });

    window.addEventListener("pagehide", () => {
        notificationSocket?.close();
        activeSocket?.close();
    }, { once: true });
}

initializeNavigation();
initializeVideoLikes();
initializeComments();
initializeConversationDetail();
initializePanels();