import {
  FrontendRenderer,
  FrontendRendererArgs,
} from "@streamlit/component-v2-lib";

import { StrictMode } from "react";
import { createRoot, Root } from "react-dom/client";

import MyComponent, {
  MyComponentDataShape,
  MyComponentStateShape,
} from "./MyComponent";

import "./index.css";

const reactRoots: WeakMap<
  FrontendRendererArgs["parentElement"],
  Root
> = new WeakMap();

const MyComponentRoot: FrontendRenderer<
  MyComponentStateShape,
  MyComponentDataShape
> = (args) => {
  const { data, parentElement, setTriggerValue } = args;
  console.log("[PromptGuard] Data received from Streamlit:", data);

  const rootElement = parentElement.querySelector(".react-root");

  if (!rootElement) {
    throw new Error("Unexpected: React root element not found");
  }

  let reactRoot = reactRoots.get(parentElement);

  if (!reactRoot) {
    reactRoot = createRoot(rootElement);
    reactRoots.set(parentElement, reactRoot);
  }

  const {
    name,
    items,
    detection_result,
    detection_response_id,
  } = data;
console.log("[PromptGuard] Raw component data:", data);

  reactRoot.render(
    <StrictMode>
      <MyComponent
        name={name}
        items={items}
        detection_result={detection_result}
        detection_response_id={detection_response_id}
        setTriggerValue={setTriggerValue}
      />
    </StrictMode>
  );

  return () => {
    const root = reactRoots.get(parentElement);

    if (root) {
      root.unmount();
      reactRoots.delete(parentElement);
    }
  };
};

export default MyComponentRoot;