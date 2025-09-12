import { cn } from "@/lib/utils"

function Skeleton({
  className,
  variant = 'default',
  ...props
}: React.HTMLAttributes<HTMLDivElement> & {
  variant?: 'default' | 'wave' | 'pulse'
}) {
  return (
    <div
      className={cn(
        "rounded-md bg-muted",
        {
          'animate-pulse': variant === 'default',
          'animate-pulse bg-gradient-to-r from-muted via-muted/50 to-muted bg-[length:200%_100%] animate-[shimmer_1.5s_ease-in-out_infinite]': variant === 'wave',
          'animate-pulse bg-gradient-to-r from-muted to-muted/50': variant === 'pulse',
        },
        className
      )}
      {...props}
    />
  )
}

export { Skeleton }
