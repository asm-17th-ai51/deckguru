import { m } from 'motion/react';

export function BrandMark() {
  return (
    <m.div
      className="flex cursor-default flex-col"
      transition={{
        duration: 0.12,
        ease: 'easeOut',
      }}
      whileHover={{ y: -4, scale: 1.08 }}>
      <h1 className="text-xl">DECK</h1>
      <h1 className="text-xl">GURU</h1>
    </m.div>
  );
}
