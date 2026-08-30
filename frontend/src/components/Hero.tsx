import { useRef, useMemo } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import * as THREE from 'three'

/* ── Geometric Core (Tesseract-like object) ── */
function AICore() {
  const groupRef = useRef<THREE.Group>(null)
  const { pointer } = useThree()
  const targetRotation = useRef({ x: 0, y: 0 })

  useFrame((_, delta) => {
    if (!groupRef.current) return

    // Smooth mouse follow
    targetRotation.current.x += (pointer.y * 0.3 - targetRotation.current.x) * 2 * delta
    targetRotation.current.y += (pointer.x * 0.5 - targetRotation.current.y) * 2 * delta

    groupRef.current.rotation.x = targetRotation.current.x + Math.sin(Date.now() * 0.0003) * 0.05
    groupRef.current.rotation.y += 0.002
    groupRef.current.rotation.z = targetRotation.current.x * 0.15

    // Floating motion
    groupRef.current.position.y = Math.sin(Date.now() * 0.0008) * 0.15
  })

  const goldColor = useMemo(() => new THREE.Color('#C9A84C'), [])
  const darkColor = useMemo(() => new THREE.Color('#111111'), [])

  return (
    <group ref={groupRef}>
      {/* Inner octahedron */}
      <mesh>
        <octahedronGeometry args={[0.7, 0]} />
        <meshStandardMaterial
          color={darkColor}
          emissive={goldColor}
          emissiveIntensity={0.3}
          roughness={0.15}
          metalness={0.95}
          wireframe={false}
        />
      </mesh>

      {/* Outer wireframe icosahedron */}
      <mesh>
        <icosahedronGeometry args={[1.1, 0]} />
        <meshStandardMaterial
          color={goldColor}
          emissive={goldColor}
          emissiveIntensity={0.15}
          roughness={0.3}
          metalness={0.8}
          wireframe={true}
          transparent={true}
          opacity={0.6}
        />
      </mesh>

      {/* Outer wireframe dodecahedron */}
      <mesh>
        <dodecahedronGeometry args={[1.4, 0]} />
        <meshStandardMaterial
          color={goldColor}
          emissive={goldColor}
          emissiveIntensity={0.1}
          roughness={0.4}
          metalness={0.7}
          wireframe={true}
          transparent={true}
          opacity={0.25}
        />
      </mesh>

      {/* Inner glow sphere */}
      <mesh>
        <sphereGeometry args={[0.4, 16, 16]} />
        <meshStandardMaterial
          color={goldColor}
          emissive={goldColor}
          emissiveIntensity={1.2}
          transparent={true}
          opacity={0.15}
        />
      </mesh>
    </group>
  )
}

/* ── Concentric Rings ── */
function EnvironmentRings() {
  const ringRef1 = useRef<THREE.Mesh>(null)
  const ringRef2 = useRef<THREE.Mesh>(null)
  const ringRef3 = useRef<THREE.Mesh>(null)

  const goldColor = useMemo(() => new THREE.Color('#C9A84C'), [])

  useFrame(() => {
    if (ringRef1.current) ringRef1.current.rotation.z += 0.001
    if (ringRef2.current) ringRef2.current.rotation.z -= 0.0007
    if (ringRef3.current) ringRef3.current.rotation.z += 0.0005
  })

  return (
    <group>
      <mesh ref={ringRef1} rotation={[Math.PI * 0.45, 0, 0]}>
        <torusGeometry args={[2.0, 0.008, 8, 128]} />
        <meshStandardMaterial
          color={goldColor}
          emissive={goldColor}
          emissiveIntensity={0.4}
          transparent={true}
          opacity={0.35}
        />
      </mesh>
      <mesh ref={ringRef2} rotation={[Math.PI * 0.55, Math.PI * 0.3, 0]}>
        <torusGeometry args={[2.3, 0.005, 8, 128]} />
        <meshStandardMaterial
          color={goldColor}
          emissive={goldColor}
          emissiveIntensity={0.3}
          transparent={true}
          opacity={0.2}
        />
      </mesh>
      <mesh ref={ringRef3} rotation={[Math.PI * 0.35, Math.PI * 0.6, 0]}>
        <torusGeometry args={[2.6, 0.003, 8, 128]} />
        <meshStandardMaterial
          color={goldColor}
          emissive={goldColor}
          emissiveIntensity={0.2}
          transparent={true}
          opacity={0.12}
        />
      </mesh>
    </group>
  )
}

/* ── Platform Base ── */
function Platform() {
  const goldColor = useMemo(() => new THREE.Color('#C9A84C'), [])

  return (
    <group position={[0, -1.8, 0]}>
      {/* Main platform disc */}
      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <circleGeometry args={[2.2, 64]} />
        <meshStandardMaterial
          color={new THREE.Color('#0A0A0A')}
          metalness={0.9}
          roughness={0.2}
          transparent={true}
          opacity={0.6}
        />
      </mesh>
      {/* Glowing ring around platform */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.01, 0]}>
        <ringGeometry args={[2.15, 2.25, 64]} />
        <meshStandardMaterial
          color={goldColor}
          emissive={goldColor}
          emissiveIntensity={0.6}
          transparent={true}
          opacity={0.4}
        />
      </mesh>
      {/* Inner ring */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.01, 0]}>
        <ringGeometry args={[1.4, 1.43, 64]} />
        <meshStandardMaterial
          color={goldColor}
          emissive={goldColor}
          emissiveIntensity={0.3}
          transparent={true}
          opacity={0.2}
        />
      </mesh>
    </group>
  )
}

/* ── Floating Particles ── */
function Particles() {
  const particlesRef = useRef<THREE.Points>(null)
  const count = 60

  const positions = useMemo(() => {
    const pos = new Float32Array(count * 3)
    for (let i = 0; i < count; i++) {
      pos[i * 3] = (Math.random() - 0.5) * 8
      pos[i * 3 + 1] = (Math.random() - 0.5) * 6
      pos[i * 3 + 2] = (Math.random() - 0.5) * 8
    }
    return pos
  }, [])

  useFrame(() => {
    if (particlesRef.current) {
      particlesRef.current.rotation.y += 0.0002
    }
  })

  return (
    <points ref={particlesRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          args={[positions, 3]}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.02}
        color="#C9A84C"
        transparent={true}
        opacity={0.4}
        sizeAttenuation={true}
      />
    </points>
  )
}

/* ── Main Scene ── */
function Scene() {
  const goldColor = useMemo(() => new THREE.Color('#C9A84C'), [])

  return (
    <>
      {/* Lighting */}
      <ambientLight intensity={0.15} />
      <directionalLight position={[5, 5, 5]} intensity={0.4} color="#F0EDE6" />
      <pointLight position={[-3, 2, 2]} intensity={0.6} color={goldColor} distance={12} />
      <pointLight position={[3, -1, -2]} intensity={0.3} color={goldColor} distance={10} />

      {/* Core */}
      <AICore />

      {/* Environment */}
      <EnvironmentRings />
      <Platform />
      <Particles />
    </>
  )
}

/* ── Hero Component ── */
const Hero = () => {
  return (
    <section className="hero-section">
      <div className="hero-bg-layers" />

      <div className="hero-content">
        <div className="hero-inner">
          <div className="hero-text">
            <div className="hero-label">
              <span className="hero-label-text">AI Business Intelligence</span>
            </div>

            <h1 className="hero-title">
              <span style={{color:'var(--text-primary)'}}>Guide</span><span className="hero-title-accent">X</span>
            </h1>

            <p className="hero-description">
              An intelligent business assistant that understands context,
              executes actions, and verifies results.
            </p>

            <div className="hero-actions">
              <a href="/chat" className="btn-primary">
                Start Live Demo
              </a>
              <a href="#capabilities" className="btn-secondary">
                Explore Capabilities
              </a>
            </div>
          </div>

          <div className="hero-3d">
            <Canvas
              camera={{ position: [0, 0.5, 5], fov: 50 }}
              dpr={[1, 1.5]}
              gl={{ antialias: true, alpha: true }}
              style={{ background: 'transparent' }}
            >
              <Scene />
            </Canvas>
          </div>
        </div>
      </div>

      <div className="hero-scroll-hint">
        <span>Scroll</span>
        <div className="hero-scroll-hint-line" />
      </div>
    </section>
  )
}

export default Hero
