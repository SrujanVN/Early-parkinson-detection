import React, { useState } from 'react';
import { Activity, Beaker, CheckCircle } from 'lucide-react';
import Button from '../ui/Button';

interface CSVFeatureFormProps {
    onSubmit: (features: Record<string, number>) => void;
    isLoading?: boolean;
}

const featureSections = [
    {
        title: "Basic Vocal Frequencies",
        description: "Fundamental frequency measurements of voice recordings",
        features: [
            { name: 'MDVP_Fo_Hz', label: 'Avg Frequency (Fo)', description: 'Average vocal fundamental frequency (Hz)', min: 0, max: 300, step: 0.001 },
            { name: 'MDVP_Fhi_Hz', label: 'Max Frequency (Fhi)', description: 'Maximum vocal fundamental frequency (Hz)', min: 0, max: 600, step: 0.001 },
            { name: 'MDVP_Flo_Hz', label: 'Min Frequency (Flo)', description: 'Minimum vocal fundamental frequency (Hz)', min: 0, max: 300, step: 0.001 },
        ]
    },
    {
        title: "Jitter Measures",
        description: "Frequency variation (disturbance) in voice cycles",
        features: [
            { name: 'MDVP_Jitter_Percent', label: 'Jitter (%)', description: 'MDVP average jitter percentage', min: 0, max: 1, step: 0.00001 },
            { name: 'MDVP_Jitter_Abs', label: 'Jitter (Abs)', description: 'MDVP absolute jitter in microseconds', min: 0, max: 0.001, step: 0.000001 },
            { name: 'MDVP_RAP', label: 'RAP', description: 'Relative amplitude perturbation', min: 0, max: 1, step: 0.00001 },
            { name: 'MDVP_PPQ', label: 'PPQ', description: 'Five-point period perturbation quotient', min: 0, max: 1, step: 0.00001 },
            { name: 'Jitter_DDP', label: 'Jitter DDP', description: 'Average absolute difference of jitter differences', min: 0, max: 1, step: 0.00001 },
        ]
    },
    {
        title: "Shimmer Measures",
        description: "Amplitude variation (disturbance) in voice cycles",
        features: [
            { name: 'MDVP_Shimmer', label: 'Shimmer', description: 'MDVP local shimmer', min: 0, max: 1, step: 0.00001 },
            { name: 'MDVP_Shimmer_dB', label: 'Shimmer (dB)', description: 'MDVP shimmer in decibels', min: 0, max: 2, step: 0.001 },
            { name: 'Shimmer_APQ3', label: 'APQ3', description: 'Three-point amplitude perturbation quotient', min: 0, max: 1, step: 0.00001 },
            { name: 'Shimmer_APQ5', label: 'APQ5', description: 'Five-point amplitude perturbation quotient', min: 0, max: 1, step: 0.00001 },
            { name: 'MDVP_APQ', label: 'APQ', description: 'Amplitude perturbation quotient', min: 0, max: 1, step: 0.00001 },
            { name: 'Shimmer_DDA', label: 'Shimmer DDA', description: 'Average absolute shimmer differences', min: 0, max: 1, step: 0.00001 },
        ]
    },
    {
        title: "Harmonic & Dynamic Measures",
        description: "Advanced nonlinear and noise assessment markers",
        features: [
            { name: 'NHR', label: 'NHR', description: 'Noise-to-harmonics ratio', min: 0, max: 1, step: 0.00001 },
            { name: 'HNR', label: 'HNR', description: 'Harmonics-to-noise ratio', min: 0, max: 40, step: 0.001 },
            { name: 'RPDE', label: 'RPDE', description: 'Recurrence period density entropy', min: 0, max: 1, step: 0.000001 },
            { name: 'DFA', label: 'DFA', description: 'Detrended fluctuation analysis', min: 0, max: 1, step: 0.000001 },
            { name: 'spread1', label: 'Spread 1', description: 'Fundamental frequency variation spread', min: -10, max: 0, step: 0.000001 },
            { name: 'spread2', label: 'Spread 2', description: 'Fundamental frequency variation spread', min: 0, max: 1, step: 0.000001 },
            { name: 'D2', label: 'D2', description: 'Correlation dimension', min: 0, max: 5, step: 0.000001 },
            { name: 'PPE', label: 'PPE', description: 'Pitch period entropy', min: 0, max: 1, step: 0.000001 },
        ]
    }
];

const CSVFeatureForm: React.FC<CSVFeatureFormProps> = ({ onSubmit, isLoading }) => {
    const [formData, setFormData] = useState<Record<string, string>>({});

    const handleInputChange = (name: string, value: string) => {
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const loadNormalSample = () => {
        // Sample data for a Healthy (Normal) subject
        const healthySample = {
            MDVP_Fo_Hz: '197.076', MDVP_Fhi_Hz: '206.896', MDVP_Flo_Hz: '192.055',
            MDVP_Jitter_Percent: '0.00289', MDVP_Jitter_Abs: '0.00001', MDVP_RAP: '0.00166',
            MDVP_PPQ: '0.00168', Jitter_DDP: '0.00498', MDVP_Shimmer: '0.01098',
            MDVP_Shimmer_dB: '0.097', Shimmer_APQ3: '0.00563', Shimmer_APQ5: '0.00680',
            MDVP_APQ: '0.00802', Shimmer_DDA: '0.01689', NHR: '0.00339',
            HNR: '26.775', RPDE: '0.422229', DFA: '0.741367',
            spread1: '-7.348300', spread2: '0.177551', D2: '1.743867', PPE: '0.085569',
        };
        setFormData(healthySample);
    };

    const loadParkinsonsSample = () => {
        // Sample data for a Parkinson's subject (First row of generic dataset)
        const pdSample = {
            MDVP_Fo_Hz: '119.992', MDVP_Fhi_Hz: '157.302', MDVP_Flo_Hz: '74.997',
            MDVP_Jitter_Percent: '0.00784', MDVP_Jitter_Abs: '0.00007', MDVP_RAP: '0.00370',
            MDVP_PPQ: '0.00554', Jitter_DDP: '0.01109', MDVP_Shimmer: '0.04374',
            MDVP_Shimmer_dB: '0.426', Shimmer_APQ3: '0.02182', Shimmer_APQ5: '0.03130',
            MDVP_APQ: '0.02971', Shimmer_DDA: '0.06545', NHR: '0.02211',
            HNR: '21.033', RPDE: '0.414783', DFA: '0.815285',
            spread1: '-4.813031', spread2: '0.266482', D2: '2.301442', PPE: '0.284654',
        };
        setFormData(pdSample);
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        const features: Record<string, number> = {};
        featureSections.forEach(section => {
            section.features.forEach(input => {
                features[input.name] = parseFloat(formData[input.name] || '0');
            });
        });
        onSubmit(features);
    };

    return (
        <div className="w-full space-y-6">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-primary/5 p-4 rounded-xl border border-primary/10">
                <div>
                    <h3 className="text-lg font-bold text-primary flex items-center gap-2">
                        <Beaker className="w-5 h-5" />
                        Vocal Feature Assessment
                    </h3>
                    <p className="text-xs text-text/60 mt-0.5">Enter clinical measurements or select a clinical sample</p>
                </div>
                <div className="flex flex-wrap gap-2">
                    <button
                        type="button"
                        onClick={loadNormalSample}
                        className="px-3 py-1.5 text-xs font-semibold bg-success/10 text-success border border-success/20 rounded-lg hover:bg-success/20 transition-all flex items-center gap-1.5"
                    >
                        <CheckCircle className="w-3.5 h-3.5" />
                        Normal Case
                    </button>
                    <button
                        type="button"
                        onClick={loadParkinsonsSample}
                        className="px-3 py-1.5 text-xs font-semibold bg-warning/10 text-warning border border-warning/20 rounded-lg hover:bg-warning/20 transition-all flex items-center gap-1.5"
                    >
                        <Activity className="w-3.5 h-3.5" />
                        Parkinson's Case
                    </button>
                </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-8">
                <div className="max-h-[500px] overflow-y-auto pr-2 space-y-8 custom-scrollbar">
                    {featureSections.map((section, idx) => (
                        <div key={idx} className="space-y-4">
                            <div className="border-l-4 border-primary pl-3 py-1">
                                <h4 className="font-bold text-base text-text">{section.title}</h4>
                                <p className="text-xs text-text/50">{section.description}</p>
                            </div>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                {section.features.map((input) => (
                                    <div key={input.name} className="space-y-1.5">
                                        <label htmlFor={input.name} className="block text-xs font-semibold text-text/70">
                                            {input.label}
                                        </label>
                                        <input
                                            type="number"
                                            id={input.name}
                                            value={formData[input.name] || ''}
                                            onChange={(e) => handleInputChange(input.name, e.target.value)}
                                            step={input.step || 'any'}
                                            min={input.min}
                                            max={input.max}
                                            className="w-full px-3 py-2 text-sm border border-divider/50 rounded-lg bg-card focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary transition-all"
                                            placeholder={input.description}
                                            required
                                        />
                                    </div>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>

                <div className="pt-4 border-t border-divider">
                    <Button
                        type="submit"
                        fullWidth
                        size="lg"
                        variant="primary"
                        disabled={isLoading}
                        className="shadow-lg shadow-primary/20"
                    >
                        {isLoading ? (
                            <span className="flex items-center justify-center">
                                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                                Processing Clinical Data...
                            </span>
                        ) : (
                            <span className="flex items-center justify-center gap-2">
                                <Activity className="w-5 h-5" />
                                Analyze Voice Biomarkers
                            </span>
                        )}
                    </Button>
                </div>
            </form>
        </div>
    );
};

export default CSVFeatureForm;
