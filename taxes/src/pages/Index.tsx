import { Header } from "@/components/Header";
import { Hero } from "@/components/Hero";
import { TaxSlider } from "@/components/TaxSlider";
import { Services } from "@/components/Services";
import { Footer } from "@/components/Footer";

const Index = () => {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main>
        <Hero />
        <TaxSlider />
        <Services />
      </main>
      <Footer />
    </div>
  );
};

export default Index;
