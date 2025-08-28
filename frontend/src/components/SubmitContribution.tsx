import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '@/hooks/useAuth';
import { apiClient } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { Plus, Upload, Link as LinkIcon, Loader2, X } from 'lucide-react';

interface ContributionFormData {
  title: string;
  description: string;
  type: string;
  impact: string;
  evidence: {
    url: string;
    type: string;
  };
}

export const SubmitContribution = () => {
  const { isAuthenticated } = useAuth();
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const [formData, setFormData] = useState<ContributionFormData>({
    title: '',
    description: '',
    type: '',
    impact: '',
    evidence: {
      url: '',
      type: 'url'
    }
  });
  const [skills, setSkills] = useState<string[]>([]);
  const [newSkill, setNewSkill] = useState('');

  const submitContributionMutation = useMutation({
    mutationFn: (data: ContributionFormData) => apiClient.createContribution(data),
    onSuccess: () => {
      toast({
        title: "Contribution Submitted!",
        description: "Your contribution has been submitted for verification.",
      });
      // Reset form
      setFormData({
        title: '',
        description: '',
        type: '',
        impact: '',
        evidence: {
          url: '',
          type: 'url'
        }
      });
      setSkills([]);
      // Refresh contributions list
      queryClient.invalidateQueries({ queryKey: ['contributions'] });
    },
    onError: (error: Error) => {
      toast({
        title: "Submission Failed",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!isAuthenticated) {
      toast({
        title: "Authentication Required",
        description: "Please sign in to submit a contribution.",
        variant: "destructive",
      });
      return;
    }

    if (!formData.title || !formData.type || !formData.impact) {
      toast({
        title: "Missing Information",
        description: "Please fill in all required fields.",
        variant: "destructive",
      });
      return;
    }

    submitContributionMutation.mutate(formData);
  };

  const addSkill = () => {
    if (newSkill.trim() && !skills.includes(newSkill.trim())) {
      setSkills([...skills, newSkill.trim()]);
      setNewSkill('');
    }
  };

  const removeSkill = (skillToRemove: string) => {
    setSkills(skills.filter(skill => skill !== skillToRemove));
  };

  if (!isAuthenticated) {
    return (
      <Card className="shadow-card">
        <CardContent className="p-6 text-center">
          <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-3">
            <Plus className="w-6 h-6 text-primary" />
          </div>
          <h3 className="font-semibold mb-2">Sign In Required</h3>
          <p className="text-sm text-muted-foreground">
            Please connect your wallet or sign in to submit contributions.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="shadow-card">
      <CardHeader>
        <CardTitle className="text-xl">Submit New Contribution</CardTitle>
        <p className="text-muted-foreground">
          Add your work, activism, or community contribution for verification and token rewards.
        </p>
      </CardHeader>
      <CardContent className="space-y-4">
        <form onSubmit={handleSubmit}>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-semibold">Title *</label>
              <Input 
                placeholder="e.g., KRNL Hackathon Project"
                value={formData.title}
                onChange={(e) => setFormData({...formData, title: e.target.value})}
                required
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-semibold">Category *</label>
              <Select 
                value={formData.type}
                onValueChange={(value) => setFormData({...formData, type: value})}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select category" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="coding">Coding</SelectItem>
                  <SelectItem value="education">Education</SelectItem>
                  <SelectItem value="activism">Activism</SelectItem>
                  <SelectItem value="leadership">Leadership</SelectItem>
                  <SelectItem value="entrepreneurship">Entrepreneurship</SelectItem>
                  <SelectItem value="environmental">Environmental</SelectItem>
                  <SelectItem value="community">Community</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-semibold">Description</label>
            <Textarea 
              placeholder="Describe your contribution, its impact, and how it benefits the community..."
              className="min-h-[100px]"
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-semibold">Impact Level *</label>
              <Select 
                value={formData.impact}
                onValueChange={(value) => setFormData({...formData, impact: value})}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select impact" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="minimal">Minimal</SelectItem>
                  <SelectItem value="moderate">Moderate</SelectItem>
                  <SelectItem value="significant">Significant</SelectItem>
                  <SelectItem value="transformative">Transformative</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-semibold">Evidence URL</label>
              <Input 
                placeholder="GitHub repo, website, or documentation URL"
                value={formData.evidence.url}
                onChange={(e) => setFormData({
                  ...formData, 
                  evidence: {...formData.evidence, url: e.target.value}
                })}
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-semibold">Skills Used</label>
            <div className="flex flex-wrap gap-2 mb-2">
              {skills.map((skill) => (
                <Badge key={skill} variant="secondary" className="flex items-center gap-1">
                  {skill}
                  <X 
                    className="w-3 h-3 cursor-pointer hover:text-destructive" 
                    onClick={() => removeSkill(skill)}
                  />
                </Badge>
              ))}
              <div className="flex gap-2">
                <Input 
                  placeholder="Add a skill"
                  value={newSkill}
                  onChange={(e) => setNewSkill(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addSkill())}
                  className="w-32"
                />
                <Button type="button" variant="outline" size="sm" onClick={addSkill}>
                  <Plus className="w-3 h-3" />
                </Button>
              </div>
            </div>
          </div>

          <div className="bg-muted p-4 rounded-lg">
            <h4 className="font-semibold mb-2">MeTTa AI Analysis Preview</h4>
            <p className="text-sm text-muted-foreground mb-2">
              Estimated token reward: <span className="text-token-gold font-semibold">150-220 NIMO</span>
            </p>
            <p className="text-xs text-muted-foreground">
              Based on category, evidence quality, and skill match. Final reward determined after verification.
            </p>
          </div>

          <Button 
            type="submit" 
            className="w-full bg-gradient-primary"
            disabled={submitContributionMutation.isPending}
          >
            {submitContributionMutation.isPending ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Submitting...
              </>
            ) : (
              'Submit for Verification'
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};