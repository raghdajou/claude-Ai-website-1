// The Framer APIs the Codigo (AIChatPrompt) component imports, so it runs outside Framer.
export { motion, AnimatePresence } from 'framer-motion'
export const ControlType = new Proxy({}, { get: (_, key) => String(key) })
export function addPropertyControls() {}
