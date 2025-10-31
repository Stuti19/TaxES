import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';

export default function ManualForm() {
  const [fields, setFields] = useState([
    { label: 'Assessment Year (AY)', type: 'text', value: '' },
    { label: 'Filing Section & Type', type: 'text', value: '' },
    { label: 'Residential Status', type: 'text', value: '' },
    { label: 'Tax Regime', type: 'text', value: '' },
    { label: 'Email ID', type: 'email', value: '' },
    { label: 'Mobile Number', type: 'tel', value: '' },
    { label: "Father's Name", type: 'text', value: '' },
    { label: 'Employment Category', type: 'text', value: '' },
    { label: 'Income from Other Sources', type: 'number', value: '' },
    { label: 'House Property Income or Loss', type: 'number', value: '' },
    { label: 'Section 80 Deductions', type: 'number', value: '' },
    { label: 'Relief u/s 89', type: 'number', value: '' }
  ]);

  const handleChange = (index: number, newValue: string) => {
    const updated = [...fields];
    updated[index].value = newValue;
    setFields(updated);
  };

  const addField = () => {
    setFields([...fields, { label: 'New Field', type: 'text', value: '' }]);
  };

  const removeField = (index: number) => {
    const updated = fields.filter((_, i) => i !== index);
    setFields(updated);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="flex items-center justify-between px-8 py-4 bg-blue-600 text-white shadow">
        <h1 className="text-2xl font-bold">TaxES Pro</h1>
        <Button className="bg-white text-blue-600 font-semibold hover:bg-gray-200">Professional Dashboard</Button>
      </nav>

      <main className="flex flex-col items-center py-10 px-4">
        <h2 className="text-3xl font-bold text-blue-700 mb-8 text-center">Document Management Form</h2>

        <Card className="w-full max-w-3xl shadow-xl border border-gray-200 rounded-2xl">
          <CardContent className="p-6 space-y-4">
            {fields.map((field, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                whileHover={{ scale: 1.02 }}
                className="flex items-center justify-between space-x-3 border-b pb-3"
              >
                <div className="flex-1">
                  <label className="block text-sm font-medium text-gray-700">{field.label}</label>
                  <input
                    type={field.type}
                    value={field.value}
                    onChange={(e) => handleChange(index, e.target.value)}
                    className="mt-1 w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder={`Enter ${field.label}`}
                  />
                </div>
                <Button variant="destructive" onClick={() => removeField(index)}>
                  Remove
                </Button>
              </motion.div>
            ))}

            <div className="flex justify-between items-center mt-6">
              <Button onClick={addField} className="bg-green-600 hover:bg-green-700 text-white">+ Add Field</Button>
              <Button className="bg-blue-600 hover:bg-blue-700 text-white">Save Form</Button>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}