import React, { useState, useEffect } from 'react';
import SkillCard from '../components/SkillCard';

const Skills = () => {
  const [skills, setSkills] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [loading, setLoading] = useState(true);

  const categories = [
    { id: 'all', name: 'All Categories' },
    { id: 'technical', name: 'Technical' },
    { id: 'creative', name: 'Creative' },
    { id: 'business', name: 'Business' },
    { id: 'social', name: 'Social Impact' },
    { id: 'leadership', name: 'Leadership' }
  ];

  // Mock data for skills - will be replaced with API call
  useEffect(() => {
    const mockSkills = [
      {
        id: 1,
        name: 'React Development',
        category: 'technical',
        description: 'Build modern web applications with React and its ecosystem',
        level: 'intermediate',
        contributors: 24,
        avgTokens: 85,
        icon: '›'
      },
      {
        id: 2,
        name: 'UI/UX Design',
        category: 'creative',
        description: 'Design user-centered interfaces and experiences',
        level: 'intermediate',
        contributors: 18,
        avgTokens: 70,
        icon: '<¨'
      },
      {
        id: 3,
        name: 'Community Management',
        category: 'social',
        description: 'Build and manage online communities',
        level: 'beginner',
        contributors: 32,
        avgTokens: 60,
        icon: '=e'
      },
      {
        id: 4,
        name: 'Smart Contract Development',
        category: 'technical',
        description: 'Develop and deploy blockchain smart contracts',
        level: 'advanced',
        contributors: 12,
        avgTokens: 120,
        icon: '=Ü'
      },
      {
        id: 5,
        name: 'Content Creation',
        category: 'creative',
        description: 'Create engaging content for various platforms',
        level: 'beginner',
        contributors: 45,
        avgTokens: 50,
        icon: ''
      },
      {
        id: 6,
        name: 'Project Management',
        category: 'business',
        description: 'Plan, execute, and deliver projects successfully',
        level: 'intermediate',
        contributors: 28,
        avgTokens: 75,
        icon: '=Ê'
      },
      {
        id: 7,
        name: 'Environmental Advocacy',
        category: 'social',
        description: 'Promote environmental awareness and action',
        level: 'intermediate',
        contributors: 22,
        avgTokens: 65,
        icon: '<1'
      },
      {
        id: 8,
        name: 'Team Leadership',
        category: 'leadership',
        description: 'Lead and inspire teams to achieve goals',
        level: 'advanced',
        contributors: 15,
        avgTokens: 95,
        icon: '=Q'
      }
    ];

    setTimeout(() => {
      setSkills(mockSkills);
      setLoading(false);
    }, 1000);
  }, []);

  const filteredSkills = skills.filter(skill => {
    const matchesSearch = skill.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         skill.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || skill.category === selectedCategory;
    
    return matchesSearch && matchesCategory;
  });

  const handleSkillInterest = (skillId) => {
    // Mock function - would track user interest in skill
    console.log(`User expressed interest in skill ${skillId}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#020617] text-white p-6 flex items-center justify-center">
        <div className="text-blue-400">Loading skills...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#020617] text-white p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-4">Skills & Opportunities</h1>
          <p className="text-gray-400 text-lg">
            Discover skills you can contribute to and earn NIMO tokens
          </p>
        </div>

        {/* Search and Filter */}
        <div className="bg-gray-800 rounded-xl p-6 mb-8">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <input
                type="text"
                placeholder="Search skills..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white placeholder-gray-400"
              />
            </div>
            <div>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white"
              >
                {categories.map(category => (
                  <option key={category.id} value={category.id}>
                    {category.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Skills Grid */}
        {filteredSkills.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-400 text-lg">No skills found matching your criteria</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredSkills.map(skill => (
              <SkillCard 
                key={skill.id} 
                skill={skill} 
                onInterest={() => handleSkillInterest(skill.id)}
              />
            ))}
          </div>
        )}

        {/* Call to Action */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-8 mt-12 text-center">
          <h2 className="text-2xl font-bold mb-4">Don't See Your Skill?</h2>
          <p className="text-gray-200 mb-6">
            Nimo is always growing! Suggest a new skill category or contribute to existing ones.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100">
              Suggest a Skill
            </button>
            <button className="bg-transparent border-2 border-white text-white px-6 py-3 rounded-lg font-semibold hover:bg-white hover:text-blue-600">
              View My Contributions
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Skills;