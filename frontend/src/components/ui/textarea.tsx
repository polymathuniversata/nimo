import * as React from "react"

import { cn } from "@/lib/utils"

export interface TextareaProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  variant?: 'default' | 'filled' | 'outlined'
  error?: boolean
  resize?: 'none' | 'vertical' | 'horizontal' | 'both'
}

const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, variant = 'default', error = false, resize = 'vertical', ...props }, ref) => {
    return (
      <textarea
        className={cn(
          "flex min-h-[80px] w-full rounded-lg border bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 transition-all duration-200 ease-out",
          {
            'border-input focus-visible:ring-ring': variant === 'default' && !error,
            'border-0 bg-muted/50 focus-visible:ring-ring focus-visible:bg-background': variant === 'filled' && !error,
            'border-2 border-border focus-visible:ring-ring focus-visible:border-ring': variant === 'outlined' && !error,
            'border-destructive focus-visible:ring-destructive': error,
            'resize-none': resize === 'none',
            'resize-y': resize === 'vertical',
            'resize-x': resize === 'horizontal',
            'resize': resize === 'both',
          },
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Textarea.displayName = "Textarea"

export { Textarea }
