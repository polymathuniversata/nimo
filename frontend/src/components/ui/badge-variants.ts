import { cva, type VariantProps } from "class-variance-authority"

export const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-all duration-200 ease-out focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 animate-in fade-in-0 zoom-in-95",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-primary text-primary-foreground hover:bg-primary/80 shadow-sm hover:shadow-md",
        secondary:
          "border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80 shadow-sm hover:shadow-md",
        destructive:
          "border-transparent bg-destructive text-destructive-foreground hover:bg-destructive/80 shadow-sm hover:shadow-md",
        outline: "text-foreground border-border hover:bg-accent hover:text-accent-foreground",
        success: "border-transparent bg-green-500 text-white hover:bg-green-600 shadow-sm hover:shadow-md",
        warning: "border-transparent bg-yellow-500 text-white hover:bg-yellow-600 shadow-sm hover:shadow-md",
        info: "border-transparent bg-blue-500 text-white hover:bg-blue-600 shadow-sm hover:shadow-md",
        gradient: "border-transparent bg-gradient-to-r from-primary to-secondary text-white hover:from-primary/90 hover:to-secondary/90 shadow-glow hover:shadow-glow-hover",
      },
      size: {
        default: "px-2.5 py-0.5 text-xs",
        sm: "px-2 py-0.5 text-xs",
        lg: "px-3 py-1 text-sm",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

export type { VariantProps }