import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Plus, Upload, Link as LinkIcon } from 'lucide-react';

export const SubmitContribution = () => {
  return (
    <Card className="shadow-card">
      <CardHeader>
        <CardTitle className="text-xl">Submit New Contribution</CardTitle>
        <p className="text-muted-foreground">
          Add your work, activism, or community contribution for verification and token rewards.
        </p>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="text-sm font-semibold">Title</label>
            <Input placeholder="e.g., KRNL Hackathon Project" />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-semibold">Category</label>
            <Select>
              <SelectTrigger>
                <SelectValue placeholder="Select category" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="coding">Coding</SelectItem>
                <SelectItem value="community_building">Community Building</SelectItem>
                <SelectItem value="activism">Activism</SelectItem>
                <SelectItem value="education">Education</SelectItem>
                <SelectItem value="design">Design</SelectItem>
                <SelectItem value="research">Research</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="space-y-2">
          <label className="text-sm font-semibold">Description</label>
          <Textarea 
            placeholder="Describe your contribution, its impact, and how it benefits the community..."
            className="min-h-[100px]"
          />
        </div>

        <div className="space-y-2">
          <label className="text-sm font-semibold">Evidence & Links</label>
          <div className="space-y-2">
            <div className="flex gap-2">
              <Input placeholder="GitHub repo, website, or documentation URL" />
              <Button variant="outline" size="sm">
                <LinkIcon className="w-4 h-4" />
              </Button>
            </div>
            <div className="flex gap-2">
              <Input placeholder="Additional evidence URL" />
              <Button variant="outline" size="sm">
                <Upload className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>

        <div className="space-y-2">
          <label className="text-sm font-semibold">Skills Used</label>
          <div className="flex flex-wrap gap-2 mb-2">
            <Badge variant="secondary">Python</Badge>
            <Badge variant="secondary">Community Building</Badge>
            <Button variant="outline" size="sm" className="h-6">
              <Plus className="w-3 h-3 mr-1" />
              Add Skill
            </Button>
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

        <Button className="w-full bg-gradient-primary">
          Submit for Verification
        </Button>
      </CardContent>
    </Card>
  );
};