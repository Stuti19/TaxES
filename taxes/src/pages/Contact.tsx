import { Navigation } from "@/components/Navigation";
import { Footer } from "@/components/Footer";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { MapPin, Phone, Mail, Clock, MessageCircle, Send } from "lucide-react";

const Contact = () => {
  const contactInfo = [
    {
      icon: <MapPin className="h-6 w-6 text-primary" />,
      title: "Office Address",
      details: ["123 Business District", "New Delhi - 110001", "India"]
    },
    {
      icon: <Phone className="h-6 w-6 text-green-500" />,
      title: "Phone Numbers",
      details: ["+91 98765 43210", "+91 98765 43211", "Toll Free: 1800-123-4567"]
    },
    {
      icon: <Mail className="h-6 w-6 text-blue-500" />,
      title: "Email Addresses",
      details: ["support@taxes.com", "info@taxes.com", "hello@taxes.com"]
    },
    {
      icon: <Clock className="h-6 w-6 text-accent" />,
      title: "Business Hours",
      details: ["Mon - Fri: 9:00 AM - 7:00 PM", "Saturday: 10:00 AM - 4:00 PM", "Sunday: Closed"]
    }
  ];

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <main>
        {/* Hero Section */}
        <section className="py-20 relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-background to-accent/5 animate-gradient-x bg-[length:400%_400%]" />
          
          <div className="container relative">
            <div className="text-center max-w-4xl mx-auto">
              <Badge className="mb-4" variant="secondary">
                Get In Touch
              </Badge>
              <h1 className="text-4xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent">
                Contact Us
              </h1>
              <p className="text-xl text-muted-foreground mb-8 leading-relaxed">
                Have questions about our services? Need help with your tax filing? 
                Our expert team is here to assist you every step of the way.
              </p>
            </div>
          </div>
        </section>

        {/* Contact Info Grid */}
        <section className="py-20">
          <div className="container">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
              {contactInfo.map((info, index) => (
                <Card key={index} className="text-center hover:shadow-lg transition-all duration-300 hover:scale-105">
                  <CardHeader>
                    <div className="flex justify-center mb-4">
                      {info.icon}
                    </div>
                    <CardTitle className="text-lg">{info.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-1">
                      {info.details.map((detail, detailIndex) => (
                        <p key={detailIndex} className="text-sm text-muted-foreground">
                          {detail}
                        </p>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* Contact Form & Map */}
        <section className="py-20 bg-muted/50">
          <div className="container">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
              {/* Contact Form */}
              <Card>
                <CardHeader>
                  <div className="flex items-center gap-2 mb-2">
                    <MessageCircle className="h-6 w-6 text-primary" />
                    <CardTitle>Send us a Message</CardTitle>
                  </div>
                  <CardDescription>
                    Fill out the form below and we'll get back to you within 24 hours
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <form className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="text-sm font-medium mb-2 block">First Name</label>
                        <Input placeholder="Enter your first name" />
                      </div>
                      <div>
                        <label className="text-sm font-medium mb-2 block">Last Name</label>
                        <Input placeholder="Enter your last name" />
                      </div>
                    </div>
                    
                    <div>
                      <label className="text-sm font-medium mb-2 block">Email</label>
                      <Input type="email" placeholder="Enter your email address" />
                    </div>
                    
                    <div>
                      <label className="text-sm font-medium mb-2 block">Phone Number</label>
                      <Input type="tel" placeholder="Enter your phone number" />
                    </div>
                    
                    <div>
                      <label className="text-sm font-medium mb-2 block">Subject</label>
                      <Input placeholder="What's this about?" />
                    </div>
                    
                    <div>
                      <label className="text-sm font-medium mb-2 block">Message</label>
                      <Textarea 
                        placeholder="Tell us more about your inquiry..."
                        className="min-h-[120px]"
                      />
                    </div>
                    
                    <Button className="w-full" size="lg">
                      <Send className="mr-2 h-5 w-5" />
                      Send Message
                    </Button>
                  </form>
                </CardContent>
              </Card>

              {/* Map/Location */}
              <Card>
                <CardHeader>
                  <div className="flex items-center gap-2 mb-2">
                    <MapPin className="h-6 w-6 text-primary" />
                    <CardTitle>Visit Our Office</CardTitle>
                  </div>
                  <CardDescription>
                    Located in the heart of New Delhi's business district
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {/* Placeholder for map - you can integrate Google Maps or other map service */}
                  <div className="bg-muted rounded-lg h-64 flex items-center justify-center mb-6">
                    <div className="text-center">
                      <MapPin className="h-12 w-12 text-muted-foreground mx-auto mb-2" />
                      <p className="text-muted-foreground">Interactive Map</p>
                      <p className="text-sm text-muted-foreground">123 Business District, New Delhi</p>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-semibold mb-2">Directions</h4>
                      <p className="text-sm text-muted-foreground">
                        Our office is conveniently located near Connaught Place metro station. 
                        Take Exit 3 and walk 5 minutes towards the business district.
                      </p>
                    </div>
                    
                    <div>
                      <h4 className="font-semibold mb-2">Parking</h4>
                      <p className="text-sm text-muted-foreground">
                        Free parking is available in our building's basement. 
                        Visitor parking spots are available on floors B1 and B2.
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>

        {/* FAQ Section */}
        <section className="py-20">
          <div className="container">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">
                Frequently Asked Questions
              </h2>
              <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                Quick answers to common questions about our services
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
              {[
                {
                  question: "How long does ITR filing take?",
                  answer: "With our automated system, most ITR filings are completed within 24-48 hours after document submission."
                },
                {
                  question: "Is my data secure?",
                  answer: "Yes, we use bank-grade encryption and security measures to protect all your financial information."
                },
                {
                  question: "What documents do I need?",
                  answer: "You'll need your Aadhar card, Form 16, bank statements, and any investment proofs for the financial year."
                },
                {
                  question: "Do you provide support after filing?",
                  answer: "Yes, we provide complete post-filing support including responding to IT department notices and queries."
                }
              ].map((faq, index) => (
                <Card key={index} className="hover:shadow-lg transition-all duration-300">
                  <CardHeader>
                    <CardTitle className="text-lg">{faq.question}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-muted-foreground">{faq.answer}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>
      </main>
      
      <Footer />
    </div>
  );
};

export default Contact;