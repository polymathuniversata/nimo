import type { Config } from "tailwindcss";
import tailwindcssAnimate from "tailwindcss-animate";

export default {
	darkMode: ["class"],
	content: [
		"./pages/**/*.{ts,tsx}",
		"./components/**/*.{ts,tsx}",
		"./app/**/*.{ts,tsx}",
		"./src/**/*.{ts,tsx}",
	],
	prefix: "",
	theme: {
		container: {
			center: true,
			padding: '1rem',
			screens: {
				sm: '640px',
				md: '768px',
				lg: '1024px',
				xl: '1280px',
				'2xl': '1400px'
			}
		},
		screens: {
			'xs': '475px',
			'sm': '640px',
			'md': '768px',
			'lg': '1024px',
			'xl': '1280px',
			'2xl': '1536px',
			'3xl': '1920px',
		},
		extend: {
			fontSize: {
				'fluid-sm': 'clamp(0.875rem, 0.8rem + 0.375vw, 1rem)',
				'fluid-base': 'clamp(1rem, 0.9rem + 0.5vw, 1.125rem)',
				'fluid-lg': 'clamp(1.125rem, 1rem + 0.625vw, 1.25rem)',
				'fluid-xl': 'clamp(1.25rem, 1.1rem + 0.75vw, 1.5rem)',
				'fluid-2xl': 'clamp(1.5rem, 1.3rem + 1vw, 2rem)',
				'fluid-3xl': 'clamp(1.875rem, 1.5rem + 1.875vw, 2.25rem)',
				'fluid-4xl': 'clamp(2.25rem, 1.8rem + 2.25vw, 3rem)',
				'fluid-5xl': 'clamp(3rem, 2.2rem + 4vw, 4rem)',
				'fluid-6xl': 'clamp(3.75rem, 2.8rem + 4.75vw, 5rem)',
				'fluid-7xl': 'clamp(4.5rem, 3.2rem + 6.5vw, 6rem)',
				'fluid-8xl': 'clamp(6rem, 4rem + 10vw, 8rem)',
				'fluid-9xl': 'clamp(8rem, 5rem + 15vw, 10rem)',
			},
			spacing: {
				'fluid-xs': 'clamp(0.5rem, 0.4rem + 0.5vw, 0.75rem)',
				'fluid-sm': 'clamp(0.75rem, 0.6rem + 0.75vw, 1rem)',
				'fluid-md': 'clamp(1rem, 0.8rem + 1vw, 1.5rem)',
				'fluid-lg': 'clamp(1.5rem, 1.2rem + 1.5vw, 2rem)',
				'fluid-xl': 'clamp(2rem, 1.6rem + 2vw, 3rem)',
				'fluid-2xl': 'clamp(3rem, 2.4rem + 3vw, 4rem)',
				'fluid-3xl': 'clamp(4rem, 3.2rem + 4vw, 6rem)',
			},
			colors: {
				border: 'hsl(var(--border))',
				input: 'hsl(var(--input))',
				ring: 'hsl(var(--ring))',
				background: 'hsl(var(--background))',
				foreground: 'hsl(var(--foreground))',
				primary: {
					DEFAULT: 'hsl(var(--primary))',
					foreground: 'hsl(var(--primary-foreground))'
				},
				secondary: {
					DEFAULT: 'hsl(var(--secondary))',
					foreground: 'hsl(var(--secondary-foreground))'
				},
				destructive: {
					DEFAULT: 'hsl(var(--destructive))',
					foreground: 'hsl(var(--destructive-foreground))'
				},
				muted: {
					DEFAULT: 'hsl(var(--muted))',
					foreground: 'hsl(var(--muted-foreground))'
				},
				accent: {
					DEFAULT: 'hsl(var(--accent))',
					foreground: 'hsl(var(--accent-foreground))'
				},
				popover: {
					DEFAULT: 'hsl(var(--popover))',
					foreground: 'hsl(var(--popover-foreground))'
				},
				card: {
					DEFAULT: 'hsl(var(--card))',
					foreground: 'hsl(var(--card-foreground))'
				},
				// Web3 & Nimo-specific colors
				'nft-glow': 'hsl(var(--nft-glow))',
				'token-gold': 'hsl(var(--token-gold))',
				'verification-green': 'hsl(var(--verification-green))',
				'impact-blue': 'hsl(var(--impact-blue))',
				sidebar: {
					DEFAULT: 'hsl(var(--sidebar-background))',
					foreground: 'hsl(var(--sidebar-foreground))',
					primary: 'hsl(var(--sidebar-primary))',
					'primary-foreground': 'hsl(var(--sidebar-primary-foreground))',
					accent: 'hsl(var(--sidebar-accent))',
					'accent-foreground': 'hsl(var(--sidebar-accent-foreground))',
					border: 'hsl(var(--sidebar-border))',
					ring: 'hsl(var(--sidebar-ring))'
				}
			},
			borderRadius: {
				lg: 'var(--radius)',
				md: 'calc(var(--radius) - 2px)',
				sm: 'calc(var(--radius) - 4px)',
				xl: 'var(--radius-lg)',
				'2xl': 'var(--radius-xl)',
			},
			keyframes: {
				'accordion-down': {
					from: {
						height: '0'
					},
					to: {
						height: 'var(--radix-accordion-content-height)'
					}
				},
				'accordion-up': {
					from: {
						height: 'var(--radix-accordion-content-height)'
					},
					to: {
						height: '0'
					}
				},
				'pulse-glow': {
					'0%, 100%': {
						opacity: '1',
						transform: 'scale(1)'
					},
					'50%': {
						opacity: '0.8', 
						transform: 'scale(1.02)'
					}
				},
				'float': {
					'0%, 100%': {
						transform: 'translateY(0px)'
					},
					'50%': {
						transform: 'translateY(-10px)'
					}
				},
				'fade-in': {
					'0%': {
						opacity: '0',
						transform: 'translateY(20px)'
					},
					'100%': {
						opacity: '1',
						transform: 'translateY(0)'
					}
				},
				'slide-in-left': {
					'0%': {
						opacity: '0',
						transform: 'translateX(-30px)'
					},
					'100%': {
						opacity: '1',
						transform: 'translateX(0)'
					}
				},
				'slide-in-right': {
					'0%': {
						opacity: '0',
						transform: 'translateX(30px)'
					},
					'100%': {
						opacity: '1',
						transform: 'translateX(0)'
					}
				},
				'scale-in': {
					'0%': {
						opacity: '0',
						transform: 'scale(0.9)'
					},
					'100%': {
						opacity: '1',
						transform: 'scale(1)'
					}
				},
				'bounce-subtle': {
					'0%, 100%': {
						transform: 'translateY(0)'
					},
					'50%': {
						transform: 'translateY(-5px)'
					}
				}
			},
			animation: {
				'accordion-down': 'accordion-down 0.2s ease-out',
				'accordion-up': 'accordion-up 0.2s ease-out',
				'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
				'float': 'float 3s ease-in-out infinite',
				'fade-in': 'fade-in 0.6s ease-out',
				'slide-in-left': 'slide-in-left 0.6s ease-out',
				'slide-in-right': 'slide-in-right 0.6s ease-out',
				'scale-in': 'scale-in 0.4s ease-out',
				'bounce-subtle': 'bounce-subtle 2s ease-in-out infinite',
			},
			aspectRatio: {
				'auto': 'auto',
				'square': '1 / 1',
				'video': '16 / 9',
				'portrait': '3 / 4',
				'wide': '21 / 9',
				'ultrawide': '32 / 9',
			},
			maxWidth: {
				'8xl': '88rem',
				'9xl': '96rem',
			},
			gridTemplateColumns: {
				'auto-fit-xs': 'repeat(auto-fit, minmax(16rem, 1fr))',
				'auto-fit-sm': 'repeat(auto-fit, minmax(20rem, 1fr))',
				'auto-fit-md': 'repeat(auto-fit, minmax(24rem, 1fr))',
				'auto-fit-lg': 'repeat(auto-fit, minmax(28rem, 1fr))',
				'auto-fit-xl': 'repeat(auto-fit, minmax(32rem, 1fr))',
				'auto-fill-xs': 'repeat(auto-fill, minmax(16rem, 1fr))',
				'auto-fill-sm': 'repeat(auto-fill, minmax(20rem, 1fr))',
				'auto-fill-md': 'repeat(auto-fill, minmax(24rem, 1fr))',
				'auto-fill-lg': 'repeat(auto-fill, minmax(28rem, 1fr))',
				'auto-fill-xl': 'repeat(auto-fill, minmax(32rem, 1fr))',
			},
			backgroundImage: {
				'gradient-primary': 'var(--gradient-primary)',
				'gradient-nft': 'var(--gradient-nft)',
				'gradient-hero': 'var(--gradient-hero)',
			},
			boxShadow: {
				'nft': 'var(--shadow-nft)',
				'card': 'var(--shadow-card)', 
				'glow': 'var(--shadow-glow)',
				'hover': 'var(--shadow-hover)',
				'inner': 'var(--shadow-inner)',
				'xl': '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
				'2xl': '0 25px 50px -12px rgb(0 0 0 / 0.25)',
			}
		}
	},
	plugins: [tailwindcssAnimate],
};
