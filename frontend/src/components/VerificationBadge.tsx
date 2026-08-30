interface VerificationBadgeProps {
  verification: {
    goal_achieved: boolean
    reason: string
  }
}

const VerificationBadge = ({ verification }: VerificationBadgeProps) => {
  const { goal_achieved, reason } = verification

  return (
    <div className={`verification-badge ${goal_achieved ? 'verified' : 'unverified'}`}>
      <div className="verification-icon">
        {goal_achieved ? '✓' : '⚠'}
      </div>
      <div className="verification-text">
        <span className="verification-label">
          {goal_achieved ? 'Verified Successfully' : 'Verification Warning'}
        </span>
        {reason}
      </div>
    </div>
  )
}

export default VerificationBadge
