import type { FrontendRendererArgs } from "@streamlit/component-v2-lib";
import { useEffect, useRef, useState } from "react";
import type { FC, ReactElement } from "react";

import SideBar from "./components/SideBar";
import NavBar from "./components/NavBar";
import ChatWindow from "./components/ChatWindow";
import ChatInput from "./components/ChatInput";

import type { DetectionResult } from "./types/detection";
import type { Conversation, Message } from "./types/chat";

export type MyComponentStateShape = {
  prompt_submitted: string | null;
};

export type MyComponentDataShape = {
  name: string;
  items: string[];
  detection_result: DetectionResult | null;
  detection_response_id: string | null;
};

export type MyComponentProps = Pick<
  FrontendRendererArgs<MyComponentStateShape, MyComponentDataShape>,
  "setTriggerValue"
> &
  MyComponentDataShape;

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

type PendingRequest = {
  requestId: string;
  conversationId: string;
};

function getFallbackReply(result: DetectionResult): string {
  if (result.prediction === "INJECTION") {
    return "PromptGuard flagged this prompt as a potential prompt injection. The classifier identifies potentially unsafe prompts; blocking requires a separate enforcement action.";
  }

  if (result.prediction === "BENIGN") {
    return "PromptGuard classified this prompt as benign. This classifier detects prompt injection; it does not independently generate general-purpose answers.";
  }

  return result.error ?? "PromptGuard could not analyze this prompt.";
}

const MyComponent: FC<MyComponentProps> = ({
  setTriggerValue,
  detection_result,
  detection_response_id,
}): ReactElement => {
  const [conversations, setConversations] =
    useState<Conversation[]>(INITIAL_CONVERSATIONS);

  const [activeId, setActiveId] = useState<string | null>(null);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [inputError, setInputError] = useState("");
  const pendingRequestRef = useRef<PendingRequest | null>(null);

  const activeMessages =
    conversations.find((conversation) => conversation.id === activeId)
      ?.messages ?? [];

  useEffect(() => {

    if (!detection_result || !detection_response_id) {
      return;

      
    }

    const pending = pendingRequestRef.current;

    if (!pending || pending.requestId !== detection_response_id) {
      return;
    }

    pendingRequestRef.current = null;
    setIsTyping(false);

    const assistantMessage: Message = {
      id: crypto.randomUUID(),
      role: "assistant",
      content: getFallbackReply(detection_result),
      detection: detection_result,
      blocked: false,
    };

    setConversations((previous) =>
      previous.map((conversation) =>
        conversation.id === pending.conversationId
          ? {
              ...conversation,
              messages: [
                ...conversation.messages,
                assistantMessage,
              ],
            }
          : conversation
      )
    );
  }, [detection_result, detection_response_id]);

  function newChat() {
    const conversation: Conversation = {
      id: crypto.randomUUID(),
      title: "New conversation",
      messages: [],
    };

    setConversations((previous) => [
      conversation,
      ...previous,
    ]);

    setActiveId(conversation.id);
    setInput("");
  }

  function selectConversation(id: string) {
    setActiveId(id);
    setInput("");
  }

  function handleExampleClick(text: string) {
    setInput(text);
  }
  function handleInputChange(value: string) {
    setInput(value);

    if (value.trim()) {
      setInputError("");
    }
  }

  function handleSend() {
    const text = input.trim();

    if (pendingRequestRef.current !== null) {
      return;
    }

    if (!text) {
      setInputError("Please enter a prompt before sending.");
      return;
    }

    setInputError("");

    if (!text || pendingRequestRef.current !== null) {
      return;
    }

    let conversationId = activeId;
    const isNewConversation = !conversationId;

    if (!conversationId) {
      conversationId = crypto.randomUUID();
      setActiveId(conversationId);
    }

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: text,
    };

    const title =
      text.length > 36 ? `${text.slice(0, 36)}…` : text;

    setConversations((previous) => {
      const existing = previous.find(
        (conversation) => conversation.id === conversationId
      );

      if (existing) {
        return previous.map((conversation) =>
          conversation.id === conversationId
            ? {
                ...conversation,
                messages: [
                  ...conversation.messages,
                  userMessage,
                ],
              }
            : conversation
        );
      }

      return [
        {
          id: conversationId!,
          title,
          messages: [userMessage],
        },
        ...previous,
      ];
    });

    const requestId = crypto.randomUUID();

    pendingRequestRef.current = {
      requestId,
      conversationId,
    };

    setIsTyping(true);
    setInput("");

    setTriggerValue(
      "prompt_submitted",
      JSON.stringify({
        request_id: requestId,
        prompt: text,
      })
    );
  }

  return (
    <div className="flex min-h-dvh w-full flex-col overflow-hidden bg-pg-bg font-sans md:h-screen md:flex-row">
      <SideBar
        conversations={conversations}
        activeId={activeId}
        onSelect={selectConversation}
        onNewChat={newChat}
      />

      <main className="flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden">
        <NavBar />

        <ChatWindow
          messages={activeMessages}
          isTyping={
            isTyping &&
            pendingRequestRef.current?.conversationId === activeId
          }
          onExampleClick={handleExampleClick}
        />

        {inputError && (
          <p
            role="alert"
            className="break-words px-4 pb-2 text-xs text-pg-danger sm:px-6 sm:text-sm"
          >
            {inputError}
          </p>
        )}
        <ChatInput
          value={input}
          onChange={handleInputChange}
          onSend={handleSend}
        />
      </main>
    </div>
  );
};

export default MyComponent;

