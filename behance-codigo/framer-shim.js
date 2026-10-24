// The Framer APIs the Codigo (AIChatPrompt) and Filament Flower components import, so it runs outside Framer.
export { motion, AnimatePresence } from 'framer-motion'
export const ControlType = new Proxy({}, { get: (_, key) => String(key) })
export function addPropertyControls() {}
// used by the Filament Flower: outside Framer it always runs live
export function useIsStaticRenderer() { return false }
