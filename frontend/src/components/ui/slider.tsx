import * as React from "react"
import * as SliderPrimitive from "@radix-ui/react-slider"

import { cn } from "@/lib/utils"

const Slider = React.forwardRef<
  React.ElementRef<typeof SliderPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof SliderPrimitive.Root> & {
    variant?: 'default' | 'gradient' | 'minimal'
    size?: 'sm' | 'default' | 'lg'
  }
>(({ className, variant = 'default', size = 'default', ...props }, ref) => (
  <SliderPrimitive.Root
    ref={ref}
    className={cn(
      "relative flex w-full touch-none select-none items-center",
      className
    )}
    {...props}
  >
    <SliderPrimitive.Track className={cn(
      "relative grow overflow-hidden rounded-full transition-all duration-200 ease-out",
      {
        'h-1.5 bg-secondary': size === 'sm',
        'h-2 bg-secondary': size === 'default',
        'h-3 bg-secondary': size === 'lg',
      }
    )}>
      <SliderPrimitive.Range className={cn(
        "absolute h-full transition-all duration-200 ease-out",
        {
          'bg-primary': variant === 'default',
          'bg-gradient-to-r from-primary to-secondary': variant === 'gradient',
          'bg-primary/80': variant === 'minimal',
        }
      )} />
    </SliderPrimitive.Track>
    <SliderPrimitive.Thumb className={cn(
      "block rounded-full border-2 bg-background ring-offset-background transition-all duration-200 ease-out focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 hover:scale-110 active:scale-95",
      {
        'h-4 w-4 border-primary': size === 'sm',
        'h-5 w-5 border-primary': size === 'default',
        'h-6 w-6 border-primary': size === 'lg',
        'shadow-lg hover:shadow-xl': variant === 'default',
        'shadow-glow hover:shadow-glow-hover': variant === 'gradient',
        'border-muted-foreground/50': variant === 'minimal',
      }
    )} />
  </SliderPrimitive.Root>
))
Slider.displayName = SliderPrimitive.Root.displayName

export { Slider }
