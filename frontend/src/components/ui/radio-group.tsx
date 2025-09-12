import * as React from "react"
import * as RadioGroupPrimitive from "@radix-ui/react-radio-group"
import { Circle } from "lucide-react"

import { cn } from "@/lib/utils"

const RadioGroup = React.forwardRef<
  React.ElementRef<typeof RadioGroupPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof RadioGroupPrimitive.Root> & {
    orientation?: 'horizontal' | 'vertical'
  }
>(({ className, orientation = 'vertical', ...props }, ref) => {
  return (
    <RadioGroupPrimitive.Root
      className={cn(
        "grid gap-2",
        {
          'grid-cols-1': orientation === 'vertical',
          'grid-flow-col auto-cols-max gap-6': orientation === 'horizontal',
        },
        className
      )}
      {...props}
      ref={ref}
    />
  )
})
RadioGroup.displayName = RadioGroupPrimitive.Root.displayName

const RadioGroupItem = React.forwardRef<
  React.ElementRef<typeof RadioGroupPrimitive.Item>,
  React.ComponentPropsWithoutRef<typeof RadioGroupPrimitive.Item> & {
    size?: 'sm' | 'default' | 'lg'
  }
>(({ className, size = 'default', ...props }, ref) => {
  return (
    <RadioGroupPrimitive.Item
      ref={ref}
      className={cn(
        "aspect-square rounded-full border border-primary text-primary ring-offset-background focus:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 transition-all duration-200 ease-out hover:border-primary/80",
        {
          'h-3 w-3': size === 'sm',
          'h-4 w-4': size === 'default',
          'h-5 w-5': size === 'lg',
        },
        className
      )}
      {...props}
    >
      <RadioGroupPrimitive.Indicator className="flex items-center justify-center">
        <Circle className={cn(
          "fill-current text-current animate-in fade-in-0 zoom-in-95 duration-200",
          {
            'h-1.5 w-1.5': size === 'sm',
            'h-2.5 w-2.5': size === 'default',
            'h-3 w-3': size === 'lg',
          }
        )} />
      </RadioGroupPrimitive.Indicator>
    </RadioGroupPrimitive.Item>
  )
})
RadioGroupItem.displayName = RadioGroupPrimitive.Item.displayName

export { RadioGroup, RadioGroupItem }
