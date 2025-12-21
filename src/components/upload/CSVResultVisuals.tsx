import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

interface CSVResultVisualsProps {
    predictionData: {
        diagnosis: string;
        confidence: number;
        parkinsons_probability?: number;
        normal_probability?: number;
        feature_importance?: Record<string, number>;
    };
}

const CSVResultVisuals: React.FC<CSVResultVisualsProps> = ({ predictionData }) => {
    // Prepare feature importance chart data
    const featureImportanceData = Object.entries(predictionData.feature_importance || {})
        .map(([name, value]) => ({
            name: name.replace(/_/g, ' '),
            importance: (value * 100).toFixed(2),
        }))
        .sort((a, b) => Number(b.importance) - Number(a.importance));

    // Prepare probability pie chart data
    const probabilityData = [
        { name: "Parkinson's", value: (predictionData.parkinsons_probability ?? 0) * 100, color: '#f59e0b' }, // Warning color
        { name: 'Normal', value: (predictionData.normal_probability ?? 0) * 100, color: '#10b981' }, // Success color
    ];

    return (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="grid grid-cols-1 gap-6">
                {/* Probability Distribution */}
                <div className="bg-card border border-divider/50 rounded-xl p-4 shadow-sm">
                    <h4 className="text-sm font-bold mb-4 flex items-center gap-2">
                        <span className="w-2 h-4 bg-primary rounded-full"></span>
                        Probability Distribution
                    </h4>
                    <div className="h-[200px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={probabilityData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={60}
                                    outerRadius={80}
                                    paddingAngle={5}
                                    dataKey="value"
                                >
                                    {probabilityData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry.color} />
                                    ))}
                                </Pie>
                                <Tooltip
                                    formatter={(value: any) => `${Number(value).toFixed(2)}%`}
                                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
                                />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                    <div className="flex justify-center gap-6 mt-2">
                        {probabilityData.map((item, idx) => (
                            <div key={idx} className="flex items-center gap-2">
                                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }}></div>
                                <span className="text-xs font-medium text-text/70">{item.name}</span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Feature Importance */}
                <div className="bg-card border border-divider/50 rounded-xl p-4 shadow-sm">
                    <h4 className="text-sm font-bold mb-4 flex items-center gap-2">
                        <span className="w-2 h-4 bg-secondary rounded-full"></span>
                        Clinical Feature Impact
                    </h4>
                    <div className="h-[250px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={featureImportanceData} layout="vertical" margin={{ left: -10, right: 20 }}>
                                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#E2E8F0" />
                                <XAxis type="number" hide />
                                <YAxis
                                    dataKey="name"
                                    type="category"
                                    width={120}
                                    tick={{ fontSize: 10, fill: '#64748b' }}
                                    axisLine={false}
                                    tickLine={false}
                                />
                                <Tooltip
                                    formatter={(value: any) => `${value}%`}
                                    cursor={{ fill: 'rgba(59, 130, 246, 0.05)' }}
                                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
                                />
                                <Bar
                                    dataKey="importance"
                                    fill="#3b82f6"
                                    radius={[0, 4, 4, 0]}
                                    barSize={15}
                                />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                    <p className="text-[10px] text-text/40 text-center mt-2 italic">
                        *High impact features contribute more to the final diagnosis
                    </p>
                </div>
            </div>
        </div>
    );
};

export default CSVResultVisuals;
