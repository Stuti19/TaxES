import { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ChevronLeft, ChevronRight, Calculator, FileText, TrendingUp, Shield } from "lucide-react";
import taxHero from "@/assets/tax-hero-1.jpg";
import taxAutomation from "@/assets/tax-automation.jpg";
import taxServices from "@/assets/tax-services.jpg";
import taxSecurity from "@/assets/tax-security.jpg";

export const TaxSlider = () => {
  const [currentSlide, setCurrentSlide] = useState(0);

  const slides = [
    {
      title: "Smart ITR Filing Made Simple",
      subtitle: "Automate your entire tax process",
      description: "Experience the future of tax filing with our AI-powered automation that handles everything from data extraction to submission.",
      image: taxHero,
      icon: Calculator,
      color: "from-primary to-primary/80"
    },
    {
      title: "Intelligent Data Extraction",
      subtitle: "AI-powered document processing",
      description: "Our advanced algorithms automatically extract and categorize financial data from your documents, ensuring 100% accuracy.",
      image: taxAutomation,
      icon: FileText,
      color: "from-accent to-accent/80"
    },
    {
      title: "Expert Tax Advisory",
      subtitle: "Professional guidance at your fingertips",
      description: "Get personalized tax strategies and optimization tips from certified professionals to maximize your savings.",
      image: taxServices,
      icon: TrendingUp,
      color: "from-green-500 to-green-600"
    },
    {
      title: "Advanced Security",
      subtitle: "Your data is completely secure",
      description: "Enterprise-level encryption and security protocols ensure your sensitive financial information remains protected.",
      image: taxSecurity,
      icon: Shield,
      color: "from-purple-500 to-purple-600"
    }
  ];

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % slides.length);
    }, 5000);

    return () => clearInterval(timer);
  }, [slides.length]);

  const nextSlide = () => {
    setCurrentSlide((prev) => (prev + 1) % slides.length);
  };

  const prevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + slides.length) % slides.length);
  };

  return (
    <section className="py-20 bg-gradient-to-br from-background via-secondary/10 to-accent/5">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
            Revolutionizing Tax Filing
          </h2>
          <p className="text-xl text-muted-foreground">
            Discover how TaxES transforms your tax filing experience
          </p>
        </div>

        <div className="relative max-w-6xl mx-auto">
          <Card className="overflow-hidden border-0 shadow-2xl bg-card/50 backdrop-blur-sm">
            <CardContent className="p-0">
              <div className="relative h-[500px] md:h-[400px]">
                {slides.map((slide, index) => (
                  <div
                    key={index}
                    className={`absolute inset-0 transition-all duration-700 ease-in-out ${
                      index === currentSlide 
                        ? 'opacity-100 translate-x-0' 
                        : index < currentSlide 
                          ? 'opacity-0 -translate-x-full' 
                          : 'opacity-0 translate-x-full'
                    }`}
                  >
                    <div className="grid md:grid-cols-2 h-full">
                      {/* Content Side */}
                      <div className="flex flex-col justify-center p-8 md:p-12 space-y-6">
                        <div className="flex items-center gap-3 mb-2">
                          <div className={`p-3 rounded-full bg-gradient-to-r ${slide.color}`}>
                            <slide.icon className="h-6 w-6 text-white" />
                          </div>
                          <Badge variant="secondary" className="text-xs">
                            Feature #{index + 1}
                          </Badge>
                        </div>
                        
                        <div>
                          <h3 className="text-3xl md:text-4xl font-bold mb-3 text-foreground">
                            {slide.title}
                          </h3>
                          <p className={`text-lg font-medium mb-4 bg-gradient-to-r ${slide.color} bg-clip-text text-transparent`}>
                            {slide.subtitle}
                          </p>
                          <p className="text-muted-foreground leading-relaxed">
                            {slide.description}
                          </p>
                        </div>

                        {/* Progress Bar */}
                        <div className="flex gap-2">
                          {slides.map((_, idx) => (
                            <div
                              key={idx}
                              className={`h-1 flex-1 rounded-full transition-all duration-300 cursor-pointer ${
                                idx === currentSlide 
                                  ? `bg-gradient-to-r ${slide.color}` 
                                  : 'bg-muted'
                              }`}
                              onClick={() => setCurrentSlide(idx)}
                            />
                          ))}
                        </div>
                      </div>

                      {/* Image Side */}
                      <div className="relative overflow-hidden">
                        <img
                          src={slide.image}
                          alt={slide.title}
                          className="w-full h-full object-cover transition-transform duration-700 hover:scale-105"
                        />
                        <div className={`absolute inset-0 bg-gradient-to-l ${slide.color} opacity-20`} />
                      </div>
                    </div>
                  </div>
                ))}

                {/* Navigation Buttons */}
                <button
                  onClick={prevSlide}
                  className="absolute left-4 top-1/2 -translate-y-1/2 p-2 rounded-full bg-background/80 hover:bg-background transition-all duration-300 hover:scale-110 shadow-lg"
                >
                  <ChevronLeft className="h-5 w-5" />
                </button>
                
                <button
                  onClick={nextSlide}
                  className="absolute right-4 top-1/2 -translate-y-1/2 p-2 rounded-full bg-background/80 hover:bg-background transition-all duration-300 hover:scale-110 shadow-lg"
                >
                  <ChevronRight className="h-5 w-5" />
                </button>
              </div>
            </CardContent>
          </Card>

          {/* Slide Indicators */}
          <div className="flex justify-center gap-3 mt-8">
            {slides.map((slide, index) => (
              <button
                key={index}
                onClick={() => setCurrentSlide(index)}
                className={`w-3 h-3 rounded-full transition-all duration-300 ${
                  index === currentSlide 
                    ? `bg-gradient-to-r ${slide.color} scale-125` 
                    : 'bg-muted hover:bg-muted-foreground/50'
                }`}
              />
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};