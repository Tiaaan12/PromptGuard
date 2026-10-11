import { FrontendRendererArgs } from "@streamlit/component-v2-lib";
import { FC, ReactElement, useState } from "react";

import SideBar from "./components/SideBar";
import NavBar from "./components/NavBar";
import ChatWindow from "./components/ChatWindow";
import ChatInput from "./components/ChatInput";

import type { DetectionResult } from "./types/detection";
import type { Conversation, Message } from "./types/chat";

// ============================================================
// STREAMLIT COMPONENT TYPES
// ============================================================

export type MyComponentStateShape = {
  prompt_submitted: string | null;
};

export type MyComponentDataShape = {
  name: string;
  items: string[];
  detection_result: DetectionResult | null;
};

export type MyComponentProps = Pick<
  FrontendRendererArgs<MyComponentStateShape, MyComponentDataShape>,
  "setTriggerValue"
> &
  MyComponentDataShape;

// ============================================================
// SAMPLE CONVERSATIONS
// ============================================================

const INITIAL_CONVERSATIONS: Conversation[] = [
  {
    id: "c1",
    title: "What is machine learning?",
    messages: [],
  },
  {
    id: "c2",
    title: "Ignore all previous instructions",
    messages: [],
  },
  {
    id: "c3",
    title: "How does PromptGuard work?",
    messages: [],
  },
];

// ============================================================
// MAIN COMPONENT
// ============================================================

const MyComponent: FC<MyComponentProps> = ({
  setTriggerValue,
  detection_result,
}): ReactElement => {
  // ----------------------------------------------------------
  // STATE
  // ----------------------------------------------------------

  const [conversations, setConversations] = useState<Conversation[]>(
    INITIAL_CONVERSATIONS
  );

  const [activeId, setActiveId] = useState<string | null>(null);

  const [input, setInput] = useState("");

  // ----------------------------------------------------------
  // ACTIVE CONVERSATION
  // ----------------------------------------------------------

  const activeMessages =
    conversations.find(
      (conversation) => conversation.id === activeId
    )?.messages ?? [];

  // ----------------------------------------------------------
  // CREATE NEW CHAT
  // ----------------------------------------------------------

  function newChat() {
    const id = `c${Date.now()}`;

    const newConversation: Conversation = {
      id,
      title: "New conversation",
      messages: [],
    };

    setConversations((prev) => [
      newConversation,
      ...prev,
    ]);

    setActiveId(id);
    setInput("");
  }

  // ----------------------------------------------------------
  // SELECT EXISTING CONVERSATION
  // ----------------------------------------------------------

  function selectConversation(id: string) {
    setActiveId(id);
    setInput("");
  }

  // ----------------------------------------------------------
  // EXAMPLE PROMPT
  // ----------------------------------------------------------

  function handleExampleClick(text: string) {
    setInput(text);
  }

  // ----------------------------------------------------------
  // SEND MESSAGE
  // ----------------------------------------------------------

  function handleSend() {
    const text = input.trim();

    // Don't send empty prompts
    if (!text) {
      return;
    }

    let conversationId = activeId;

    // --------------------------------------------------------
    // CREATE CONVERSATION IF NONE IS ACTIVE
    // --------------------------------------------------------

    if (!conversationId) {
      conversationId = `c${Date.now()}`;

      const title =
        text.length > 36
          ? `${text.slice(0, 36)}…`
          : text;

      const newConversation: Conversation = {
        id: conversationId,
        title,
        messages: [],
      };

      setConversations((prev) => [
        newConversation,
        ...prev,
      ]);

      setActiveId(conversationId);
    }

    // --------------------------------------------------------
    // CREATE USER MESSAGE
    // --------------------------------------------------------

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: text,
    };

    // --------------------------------------------------------
    // ADD USER MESSAGE TO CURRENT CONVERSATION
    // --------------------------------------------------------

    setConversations((prev) =>
      prev.map((conversation) =>
        conversation.id === conversationId
          ? {
              ...conversation,
              messages: [
                ...conversation.messages,
                userMessage,
              ],
            }
          : conversation
      )
    );

    // --------------------------------------------------------
    // SEND PROMPT TO PYTHON / STREAMLIT / ML MODEL
    // --------------------------------------------------------

    console.log("User sent:", text);

    setTriggerValue(
      "prompt_submitted",
      text
    );

    // --------------------------------------------------------
    // CLEAR INPUT
    // --------------------------------------------------------

    setInput("");
  }

  // ==========================================================
  // UI
  // ==========================================================

  return (
    <div className="flex h-screen w-full overflow-hidden bg-pg-bg font-sans">

      {/* ======================================================
          SIDEBAR
          ====================================================== */}

      <SideBar
        conversations={conversations}
        activeId={activeId}
        onSelect={selectConversation}
        onNewChat={newChat}
      />

      {/* ======================================================
          MAIN CONTENT
          ====================================================== */}

      <main className="flex min-w-0 flex-1 flex-col overflow-hidden">

        {/* ----------------------------------------------------
            NAVBAR
            ---------------------------------------------------- */}

        <NavBar />

        {/* ----------------------------------------------------
            CHAT WINDOW
            ---------------------------------------------------- */}

        <ChatWindow
          messages={activeMessages}
          isTyping={false}
          onExampleClick={handleExampleClick}
          detectionResult={detection_result}
        />

        {/* ----------------------------------------------------
            CHAT INPUT
            ---------------------------------------------------- */}

        <ChatInput
          value={input}
          onChange={setInput}
          onSend={handleSend}
        />

        

      </main>
    </div>
  );
};

export default MyComponent;