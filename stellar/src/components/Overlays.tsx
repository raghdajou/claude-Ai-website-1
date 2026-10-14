import { Check, CheckCircle2, Rocket } from "lucide-react";
import type { ReactNode } from "react";

export type TabId = "analyse" | "train" | "testing" | "deploy";

function OverlayCard({ children }: { children: ReactNode }) {
  return (
    <div className="animate-fade-in-overlay absolute inset-0 bg-black/20" style={{ opacity: 0 }}>
      <div
        className="animate-slide-up-overlay absolute left-1/2 top-1/2 w-[calc(100%-2rem)] max-w-md rounded-2xl bg-white p-5 text-left shadow-2xl sm:p-6"
        style={{ opacity: 0 }}
      >
        {children}
      </div>
    </div>
  );
}

function Progress({ value, color, label }: { value: number; color: string; label: string }) {
  return (
    <div
      className="h-2 w-full overflow-hidden rounded-full bg-gray-100"
      role="progressbar"
      aria-valuenow={value}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={label}
    >
      <div className={`h-full rounded-full ${color}`} style={{ width: `${value}%` }} />
    </div>
  );
}

const WORKSPACE_STEPS = ["Connect your tools", "Import your data", "Choose AI models", "Invite your team"];

function AnalyseOverlay() {
  return (
    <OverlayCard>
      <div className="mb-1 flex items-center justify-between text-xs font-medium text-gray-500">
        <span>Step 1 of 4</span>
        <span>25%</span>
      </div>
      <h3 className="mb-3 text-lg font-semibold text-black">Set Up Your AI Workspace</h3>
      <Progress value={25} color="bg-purple-500" label="Workspace setup progress" />
      <ol className="mt-4 space-y-2">
        {WORKSPACE_STEPS.map((step, i) => (
          <li
            key={step}
            className={`flex items-center gap-3 rounded-lg px-3 py-2 text-sm ${
              i === 0 ? "bg-purple-50 font-medium text-purple-700" : "text-gray-500"
            }`}
          >
            <span
              className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-semibold ${
                i === 0 ? "bg-purple-500 text-white" : "border border-gray-300"
              }`}
            >
              {i + 1}
            </span>
            {step}
          </li>
        ))}
      </ol>
    </OverlayCard>
  );
}

const TRAINING_METRICS = [
  { label: "Accuracy", value: "94.2%" },
  { label: "Loss", value: "0.084" },
  { label: "Samples", value: "12.4K" },
  { label: "Time left", value: "6 min" },
];

function TrainOverlay() {
  return (
    <OverlayCard>
      <div className="mb-1 flex items-center justify-between text-xs font-medium text-gray-500">
        <span>Epoch 8 of 12</span>
        <span>67%</span>
      </div>
      <h3 className="mb-3 text-lg font-semibold text-black">AI Model Training</h3>
      <Progress value={67} color="bg-orange-500" label="Training progress" />
      <dl className="mt-4 grid grid-cols-2 gap-3">
        {TRAINING_METRICS.map(({ label, value }) => (
          <div key={label} className="rounded-lg bg-gray-50 px-3 py-2">
            <dt className="text-xs text-gray-500">{label}</dt>
            <dd className="text-base font-semibold text-black">{value}</dd>
          </div>
        ))}
      </dl>
    </OverlayCard>
  );
}

const TEST_GROUPS = [
  { label: "Unit tests", passed: 84 },
  { label: "Integration tests", passed: 31 },
  { label: "End-to-end tests", passed: 12 },
];

function TestingOverlay() {
  return (
    <OverlayCard>
      <h3 className="mb-3 text-lg font-semibold text-black">Test Suite Results</h3>
      <div className="flex items-center gap-3 rounded-lg bg-green-50 px-3 py-3">
        <CheckCircle2 className="h-6 w-6 shrink-0 text-green-600" aria-hidden="true" />
        <div>
          <p className="text-sm font-semibold text-green-800">All tests passed</p>
          <p className="text-xs text-green-700">127/127 tests · 0 failures</p>
        </div>
      </div>
      <ul className="mt-4 space-y-2">
        {TEST_GROUPS.map(({ label, passed }) => (
          <li key={label} className="flex items-center justify-between text-sm">
            <span className="flex items-center gap-2 text-gray-700">
              <Check className="h-4 w-4 text-green-600" aria-hidden="true" />
              {label}
            </span>
            <span className="font-medium text-black">
              {passed}/{passed}
            </span>
          </li>
        ))}
      </ul>
    </OverlayCard>
  );
}

const DEPLOY_CHECKLIST = ["All tests passing", "Security scan complete", "Environment configured", "Rollback plan ready"];

function DeployOverlay() {
  return (
    <OverlayCard>
      <h3 className="mb-1 text-lg font-semibold text-black">Deploy to Production</h3>
      <p className="mb-4 text-sm text-gray-500">Everything checks out. You're ready to ship.</p>
      <ul className="space-y-2">
        {DEPLOY_CHECKLIST.map((item) => (
          <li key={item} className="flex items-center gap-3 text-sm text-gray-700">
            <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-black">
              <Check className="h-3 w-3 text-white" strokeWidth={3} aria-hidden="true" />
            </span>
            {item}
          </li>
        ))}
      </ul>
      <button
        type="button"
        className="mt-5 flex w-full items-center justify-center gap-2 rounded-full bg-black px-5 py-2.5 text-sm font-medium text-white transition-colors hover:bg-gray-800"
      >
        <Rocket className="h-4 w-4" aria-hidden="true" />
        Deploy Now
      </button>
    </OverlayCard>
  );
}

export default function Overlay({ tab }: { tab: TabId }) {
  switch (tab) {
    case "analyse":
      return <AnalyseOverlay />;
    case "train":
      return <TrainOverlay />;
    case "testing":
      return <TestingOverlay />;
    case "deploy":
      return <DeployOverlay />;
  }
}
