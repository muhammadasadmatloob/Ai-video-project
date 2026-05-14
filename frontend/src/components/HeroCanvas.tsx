import { Canvas, useFrame } from '@react-three/fiber';
import { Points, PointMaterial } from '@react-three/drei';
import { useState, useRef } from 'react';
import * as THREE from 'three';
import * as random from 'maath/random/dist/maath-random.esm';

function Stars() {
  // 1. Explicitly type the Ref as THREE.Points
  const ref = useRef<THREE.Points>(null!);
  
  // 2. State is explicitly typed as Float32Array
  const [sphere] = useState<Float32Array>(() => {
    const data = random.inSphere(new Float32Array(5000), { radius: 1.5 });
    return data;
  });

  // 3. Delta-based rotation for consistent speed on all monitors (60Hz vs 144Hz)
  useFrame((_state, delta) => {
    if (ref.current) {
      ref.current.rotation.x -= delta / 10;
      ref.current.rotation.y -= delta / 15;
    }
  });

  return (
    <group rotation={[0, 0, Math.PI / 4]}>
      <Points ref={ref} positions={sphere} stride={3} frustumCulled={false}>
        <PointMaterial 
          transparent 
          color="#6366f1" 
          size={0.005} 
          sizeAttenuation={true} 
          depthWrite={false} 
        />
      </Points>
    </group>
  );
}

export default function HeroCanvas() {
  return (
    <div className="fixed inset-0 -z-10 bg-slate-950">
      <Canvas camera={{ position: [0, 0, 1] }}>
        <Stars />
      </Canvas>
    </div>
  );
}