import React from 'react';

const SkillCard = ({ skill, onInterest }) => {
  const getLevelColor = (level) => {
    switch (level) {
      case 'beginner': return 'bg-green-500';
      case 'intermediate': return 'bg-yellow-500';
      case 'advanced': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getLevelText = (level) => {
    switch (level) {
      case 'beginner': return 'Beginner Friendly';
      case 'intermediate': return 'Intermediate';
      case 'advanced': return 'Advanced';
      default: return 'All Levels';
    }
  };

  return (
    <div className="bg-gray-800 rounded-xl p-6 hover:bg-gray-700 transition-colors group">
      {/* Skill Icon and Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="text-3xl">{skill.icon}</div>
        <div className={`${getLevelColor(skill.level)} text-white px-2 py-1 rounded-full text-xs font-semibold`}>
          {getLevelText(skill.level)}
        </div>
      </div>

      {/* Skill Name */}
      <h3 className="text-xl font-bold mb-2 group-hover:text-blue-400 transition-colors">
        {skill.name}
      </h3>

      {/* Description */}
      <p className="text-gray-400 text-sm mb-4 line-clamp-2">
        {skill.description}
      </p>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="text-center">
          <div className="text-lg font-semibold text-blue-400">{skill.contributors}</div>
          <div className="text-xs text-gray-500">Contributors</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-semibold text-yellow-400">{skill.avgTokens}</div>
          <div className="text-xs text-gray-500">Avg Tokens</div>
        </div>
      </div>

      {/* Action Button */}
      <button
        onClick={() => onInterest && onInterest()}
        className="w-full bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded-lg font-semibold transition-colors group-hover:bg-blue-400"
      >
        I'm Interested
      </button>
    </div>
  );
};

export default SkillCard;