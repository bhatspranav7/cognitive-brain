import { useState } from "react";

interface Props {
  onRate: (rating: number) => void;
  rated?: number;
}

export default function StarRating({ onRate, rated }: Props) {
  const [hover, setHover] = useState(0);

  if (rated) {
    return (
      <div className="star-rating done">
        {[1, 2, 3, 4, 5].map((n) => (
          <span key={n} className={n <= rated ? "star filled" : "star"}>
            ★
          </span>
        ))}
        <span className="star-thanks">thanks — feeds adaptive retrieval</span>
      </div>
    );
  }

  return (
    <div className="star-rating">
      <span className="star-label">Rate this answer:</span>
      {[1, 2, 3, 4, 5].map((n) => (
        <button
          key={n}
          className={`star ${n <= hover ? "filled" : ""}`}
          onMouseEnter={() => setHover(n)}
          onMouseLeave={() => setHover(0)}
          onClick={() => onRate(n)}
          aria-label={`Rate ${n} star${n > 1 ? "s" : ""}`}
        >
          ★
        </button>
      ))}
    </div>
  );
}
