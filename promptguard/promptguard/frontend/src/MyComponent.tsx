import { FrontendRendererArgs } from "@streamlit/component-v2-lib";

import {
  FC,
  ReactElement,
  useState,
} from "react";

import SideBar from "./components/SideBar";
import NavBar from "./components/NavBar";
import ChatInput from "./components/ChatInput";

import type { Conversation } from "../types/chat";


export type MyComponentStateShape = {};

export type MyComponentDataShape = {
  name: string;
  items: string[];
};

export type MyComponentProps = Pick<
  FrontendRendererArgs<
    MyComponentStateShape,
    MyComponentDataShape
  >,
  "setStateValue" | "setTriggerValue"
> &
  MyComponentDataShape;


const MyComponent: FC<MyComponentProps> = ({
  name,
  items,
  setStateValue,
  setTriggerValue,
}): ReactElement => {

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


 
  const [conversations, setConversations] =
    useState<Conversation[]>(INITIAL_CONVERSATIONS);

  const [activeId, setActiveId] =
    useState<string | null>(null);



  const [input, setInput] =
    useState("");


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


  function selectConversation(id: string) {
    setActiveId(id);
  }


  function handleSend() {

    const text = input.trim();

    if (!text) {
      return;
    }

    console.log("User sent:", text);

    setInput("");
  }


  return (
    <div className="
      flex
      h-screen
      w-full
      bg-pg-bg
      font-sans
      overflow-hidden
    ">

      <SideBar
        conversations={conversations}
        activeId={activeId}
        onSelect={selectConversation}
        onNewChat={newChat}
      />


      <main className="
        min-w-0
        flex
        flex-1
        flex-col
        overflow-hidden
      ">

        <NavBar />


    
        <div className="flex-1" />


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