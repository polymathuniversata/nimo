import React, { useState, useEffect } from 'react';
import ContributionCard from '../components/ContributionCard';

const Contributions = ({ user }) => {
  const [contributions, setContributions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    contribution_type: 'coding',
    evidence: '',
    impact_level: 'moderate'
  });

  // Mock data for now - will be replaced with API call
  useEffect(() => {
    const mockContributions = [
      {
        id: 1,
        title: "Open Source React Component Library",
        description: "Created a comprehensive React component library for the community",
        contribution_type: "coding",
        impact_level: "significant",
        evidence: { url: "https://github.com/user/react-library", type: "github" },
        status: "verified",
        created_at: "2024-01-15T10:30:00Z",
        verifications: [{
          organization: "Nimo Platform",
          verifier_name: "MeTTa Agent",
          comments: "Excellent contribution with strong community impact"
        }]
      },
      {
        id: 2,
        title: "Community Coding Workshop",
        description: "Organized and led a 2-day coding workshop for beginners",
        contribution_type: "education",
        impact_level: "moderate",
        evidence: { url: "https://example.com/workshop-photos", type: "website" },
        status: "pending",
        created_at: "2024-01-20T14:00:00Z",
        verifications: []
      }
    ];

    setTimeout(() => {
      setContributions(mockContributions);
      setLoading(false);
    }, 1000);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Mock API call - replace with actual API integration
    const newContribution = {
      id: contributions.length + 1,
      ...formData,
      evidence: { url: formData.evidence, type: 'website' },
      status: 'pending',
      created_at: new Date().toISOString(),
      verifications: []
    };

    setContributions([newContribution, ...contributions]);
    setShowAddModal(false);
    setFormData({
      title: '',
      description: '',
      contribution_type: 'coding',
      evidence: '',
      impact_level: 'moderate'
    });
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#020617] text-white p-6 flex items-center justify-center">
        <div className="text-blue-400">Loading contributions...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#020617] text-white p-6">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">My Contributions</h1>
          <button
            onClick={() => setShowAddModal(true)}
            className="bg-blue-500 hover:bg-blue-600 px-6 py-2 rounded-lg font-semibold"
          >
            Add Contribution
          </button>
        </div>

        {contributions.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-400 text-lg mb-4">No contributions yet</p>
            <button
              onClick={() => setShowAddModal(true)}
              className="bg-blue-500 hover:bg-blue-600 px-6 py-3 rounded-lg font-semibold"
            >
              Add Your First Contribution
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {contributions.map(contribution => (
              <ContributionCard key={contribution.id} contribution={contribution} />
            ))}
          </div>
        )}

        {/* Add Contribution Modal */}
        {showAddModal && (
          <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
            <div className="bg-gray-800 rounded-xl max-w-2xl w-full p-6 max-h-90vh overflow-y-auto">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold">Add New Contribution</h2>
                <button
                  onClick={() => setShowAddModal(false)}
                  className="text-gray-400 hover:text-white text-2xl"
                >
                  ×
                </button>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-gray-300 mb-2">Title *</label>
                  <input
                    type="text"
                    name="title"
                    value={formData.title}
                    onChange={handleChange}
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white"
                    placeholder="Enter contribution title"
                    required
                  />
                </div>

                <div>
                  <label className="block text-gray-300 mb-2">Description</label>
                  <textarea
                    name="description"
                    value={formData.description}
                    onChange={handleChange}
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white"
                    placeholder="Describe your contribution"
                    rows="4"
                  />
                </div>

                <div>
                  <label className="block text-gray-300 mb-2">Type *</label>
                  <select
                    name="contribution_type"
                    value={formData.contribution_type}
                    onChange={handleChange}
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white"
                    required
                  >
                    <option value="coding">Coding</option>
                    <option value="education">Education</option>
                    <option value="volunteer">Volunteer</option>
                    <option value="activism">Activism</option>
                    <option value="leadership">Leadership</option>
                    <option value="entrepreneurship">Entrepreneurship</option>
                    <option value="environmental">Environmental</option>
                    <option value="community">Community</option>
                  </select>
                </div>

                <div>
                  <label className="block text-gray-300 mb-2">Impact Level</label>
                  <select
                    name="impact_level"
                    value={formData.impact_level}
                    onChange={handleChange}
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white"
                  >
                    <option value="minimal">Minimal</option>
                    <option value="moderate">Moderate</option>
                    <option value="significant">Significant</option>
                    <option value="transformative">Transformative</option>
                  </select>
                </div>

                <div>
                  <label className="block text-gray-300 mb-2">Evidence URL</label>
                  <input
                    type="url"
                    name="evidence"
                    value={formData.evidence}
                    onChange={handleChange}
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white"
                    placeholder="Link to evidence (GitHub, website, etc.)"
                  />
                </div>

                <div className="flex gap-4 pt-4">
                  <button
                    type="submit"
                    className="flex-1 bg-blue-500 hover:bg-blue-600 text-white py-3 rounded-lg font-semibold"
                  >
                    Add Contribution
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowAddModal(false)}
                    className="flex-1 bg-gray-600 hover:bg-gray-700 text-white py-3 rounded-lg font-semibold"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Contributions;