import { Button } from '@/components/ui/button';
import { m } from 'motion/react';

interface ExampleQuestionChipsProps {
  questions: string[];
  onQuestionClick: (question: string) => void;
}

export function ExampleQuestionChips({
  questions,
  onQuestionClick,
}: ExampleQuestionChipsProps) {
  return (
    <div className="flex flex-wrap items-center justify-center gap-2">
      {questions.map((question, index) => (
        <m.div
          key={question}
          initial={{ opacity: 0, y: 6, scale: 0.96 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{
            delay: index * 0.06,
            duration: 0.24,
            ease: 'easeOut',
          }}
          whileHover={{
            x: 2,
            y: 1,
            scale: 0.96,
            transition: { delay: 0, duration: 0.12, ease: 'easeOut' },
          }}
          whileTap={{
            x: 2,
            y: 3,
            scale: 0.96,
            transition: { delay: 0, duration: 0.12, ease: 'easeOut' },
          }}>
          <Button
            type="button"
            variant="secondary"
            size="lg"
            onClick={() => onQuestionClick(question)}
            className="text-center">
            {question}
          </Button>
        </m.div>
      ))}
    </div>
  );
}
