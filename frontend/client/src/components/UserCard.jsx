import React from 'react';

const UserCard = ({ user, showStats = true, compact = false }) => {
  const getInitials = (name) => {
    if (!name) return 'U';
    return name.split(' ').map(n => n.charAt(0).toUpperCase()).join('').slice(0, 2);
  };

  const getReputationLevel = (score) => {
    if (score >= 90) return { level: 'Expert', color: 'text-purple-400' };
    if (score >= 70) return { level: 'Experienced', color: 'text-blue-400' };
    if (score >= 50) return { level: 'Intermediate', color: 'text-green-400' };
    if (score >= 25) return { level: 'Beginner', color: 'text-yellow-400' };
    return { level: 'New', color: 'text-gray-400' };
  };

  const reputation = getReputationLevel(user.reputationScore || 0);

  if (compact) {
    return (
      <div className="bg-gray-800 rounded-lg p-4 hover:bg-gray-700 transition-colors">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-sm font-bold">
            {getInitials(user.name)}
          </div>
          <div className="flex-1 min-w-0">
            <h4 className="font-semibold truncate">{user.name || 'Anonymous'}</h4>
            <p className={`text-sm ${reputation.color}`}>{reputation.level}</p>
          </div>
          {showStats && (
            <div className="text-right">
              <div className="text-sm font-semibold text-yellow-400">
                {user.tokenBalance || 0} NIMO
              </div>
              <div className="text-xs text-gray-500">
                {user.contributions || 0} contribs
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-xl p-6 hover:bg-gray-700 transition-colors group">
      {/* User Avatar and Basic Info */}
      <div className="flex items-start gap-4 mb-4">
        <div className="w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center text-xl font-bold flex-shrink-0">
          {getInitials(user.name)}
        </div>
        
        <div className="flex-1 min-w-0">
          <h3 className="text-xl font-bold mb-1 group-hover:text-blue-400 transition-colors">
            {user.name || 'Anonymous User'}
          </h3>
          
          <p className={`text-sm font-semibold mb-1 ${reputation.color}`}>
            {reputation.level}
          </p>
          
          {user.location && (
            <p className="text-gray-400 text-sm mb-2">=Í {user.location}</p>
          )}
          
          {user.bio && (
            <p className="text-gray-300 text-sm line-clamp-2">{user.bio}</p>
          )}
        </div>
      </div>

      {/* Skills */}
      {user.skills && user.skills.length > 0 && (
        <div className="mb-4">
          <div className="flex flex-wrap gap-1">
            {user.skills.slice(0, 4).map((skill, index) => (
              <span
                key={index}
                className="bg-blue-500 text-white px-2 py-1 rounded-full text-xs"
              >
                {skill}
              </span>
            ))}
            {user.skills.length > 4 && (
              <span className="bg-gray-600 text-white px-2 py-1 rounded-full text-xs">
                +{user.skills.length - 4}
              </span>
            )}
          </div>
        </div>
      )}

      {/* Stats */}
      {showStats && (
        <div className="grid grid-cols-3 gap-4 mb-4">
          <div className="text-center">
            <div className="text-lg font-semibold text-blue-400">
              {user.contributions || 0}
            </div>
            <div className="text-xs text-gray-500">Contributions</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-semibold text-yellow-400">
              {user.tokenBalance || 0}
            </div>
            <div className="text-xs text-gray-500">NIMO Tokens</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-semibold text-purple-400">
              {user.reputationScore || 0}
            </div>
            <div className="text-xs text-gray-500">Reputation</div>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-2">
        <button className="flex-1 bg-blue-500 hover:bg-blue-600 text-white py-2 px-3 rounded-lg text-sm font-semibold transition-colors">
          View Profile
        </button>
        <button className="bg-gray-600 hover:bg-gray-500 text-white py-2 px-3 rounded-lg text-sm font-semibold transition-colors">
          Connect
        </button>
      </div>
    </div>
  );
};

export default UserCard;