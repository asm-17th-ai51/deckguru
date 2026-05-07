import { WarningIcon } from '@phosphor-icons/react';

import { SectionEyebrow } from './recommendation-result-shared';

export function WarningsPanel({ warnings }: { warnings: string[] }) {
  if (warnings.length === 0) {
    return null;
  }

  return (
    <section
      className="border-4 border-destructive/70 bg-destructive/10 p-5 shadow-[8px_8px_0_0_rgb(0_0_0/0.45)]"
      aria-labelledby="recommendation-warnings-title">
      <SectionEyebrow icon={WarningIcon}>WARNING</SectionEyebrow>
      <h2
        id="recommendation-warnings-title"
        className="mt-3 font-galmuri11 text-base font-bold text-foreground">
        확인이 필요한 안내
      </h2>
      <ul className="mt-3 flex flex-col gap-2">
        {warnings.map((warning) => (
          <li className="text-sm leading-6 text-foreground/90" key={warning}>
            {warning}
          </li>
        ))}
      </ul>
    </section>
  );
}
