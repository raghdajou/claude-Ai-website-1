// The three Framer APIs the Swellcastpro component imports, so it runs outside Framer.
export const ControlType = new Proxy({}, { get: (_, key) => String(key) })
export function addPropertyControls() {}
export function useIsStaticRenderer() { return false }
