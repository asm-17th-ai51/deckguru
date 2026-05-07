'use client';

import { type PropsWithChildren } from 'react';

import { domAnimation, LazyMotion } from 'motion/react';

export function MotionProvider({ children }: PropsWithChildren) {
  return (
    <LazyMotion strict features={domAnimation}>
      {children}
    </LazyMotion>
  );
}
