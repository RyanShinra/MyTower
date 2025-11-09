export type Maybe<T> = T | null;
export type InputMaybe<T> = Maybe<T>;
export type Exact<T extends { [key: string]: unknown }> = { [K in keyof T]: T[K] };
export type MakeOptional<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]?: Maybe<T[SubKey]> };
export type MakeMaybe<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]: Maybe<T[SubKey]> };
export type MakeEmpty<T extends { [key: string]: unknown }, K extends keyof T> = { [_ in K]?: never };
export type Incremental<T> = T | { [P in keyof T]?: P extends ' $fragmentName' | '__typename' ? T[P] : never };
/** All built-in and custom scalars, mapped to their actual values */
export type Scalars = {
  ID: { input: string; output: string; }
  String: { input: string; output: string; }
  Boolean: { input: boolean; output: boolean; }
  Int: { input: number; output: number; }
  Float: { input: number; output: number; }
  Blocks: { input: number; output: number; }
  Meters: { input: number; output: number; }
  Pixels: { input: number; output: number; }
  Time: { input: number; output: number; }
};

export type BuildingSnapshotGql = {
  readonly __typename?: 'BuildingSnapshotGQL';
  readonly elevators: ReadonlyArray<ElevatorSnapshotGql>;
  readonly floors: ReadonlyArray<FloorSnapshotGql>;
  readonly money: Scalars['Int']['output'];
  readonly people: ReadonlyArray<PersonSnapshotGql>;
  readonly time: Scalars['Time']['output'];
};

export type ColorGql = {
  readonly __typename?: 'ColorGQL';
  readonly alpha: Scalars['Int']['output'];
  readonly blue: Scalars['Int']['output'];
  readonly green: Scalars['Int']['output'];
  readonly red: Scalars['Int']['output'];
};

export type ElevatorSnapshotGql = {
  readonly __typename?: 'ElevatorSnapshotGQL';
  readonly availableCapacity: Scalars['Int']['output'];
  readonly destinationFloor: Scalars['Int']['output'];
  readonly doorOpen: Scalars['Boolean']['output'];
  readonly horizontalPosition: Scalars['Blocks']['output'];
  readonly id: Scalars['String']['output'];
  readonly maxCapacity: Scalars['Int']['output'];
  readonly nominalDirection: VerticalDirectionGql;
  readonly passengerCount: Scalars['Int']['output'];
  readonly state: ElevatorStateGql;
  readonly verticalPosition: Scalars['Blocks']['output'];
  readonly verticalPositionMeters: Scalars['Meters']['output'];
  readonly verticalPositionPixels: Scalars['Pixels']['output'];
};

export type ElevatorStateGql =
  | 'ARRIVED'
  | 'IDLE'
  | 'LOADING'
  | 'MOVING'
  | 'READY_TO_MOVE'
  | 'UNLOADING';

export type FloorSnapshotGql = {
  readonly __typename?: 'FloorSnapshotGQL';
  readonly floorColor: ColorGql;
  readonly floorHeight: Scalars['Blocks']['output'];
  readonly floorHeightMeters: Scalars['Meters']['output'];
  readonly floorNumber: Scalars['Int']['output'];
  readonly floorType: FloorTypeGql;
  readonly floorWidth: Scalars['Blocks']['output'];
  readonly floorboardColor: ColorGql;
  readonly leftEdgeBlock: Scalars['Blocks']['output'];
  readonly personCount: Scalars['Int']['output'];
};

export type FloorTypeGql =
  | 'APARTMENT'
  | 'HOTEL'
  | 'LOBBY'
  | 'OFFICE'
  | 'RESTAURANT'
  | 'RETAIL';

export type Mutation = {
  readonly __typename?: 'Mutation';
  readonly addElevator: Scalars['String']['output'];
  readonly addElevatorBank: Scalars['String']['output'];
  readonly addElevatorBankSync: Scalars['String']['output'];
  readonly addElevatorSync: Scalars['String']['output'];
  readonly addFloor: Scalars['String']['output'];
  readonly addFloorSync: Scalars['Int']['output'];
  readonly addPerson: Scalars['String']['output'];
  readonly addPersonSync: Scalars['String']['output'];
};


export type MutationAddElevatorArgs = {
  elevatorBankId: Scalars['String']['input'];
};


export type MutationAddElevatorBankArgs = {
  hCell: Scalars['Int']['input'];
  maxFloor: Scalars['Int']['input'];
  minFloor: Scalars['Int']['input'];
};


export type MutationAddElevatorBankSyncArgs = {
  hCell: Scalars['Int']['input'];
  maxFloor: Scalars['Int']['input'];
  minFloor: Scalars['Int']['input'];
};


export type MutationAddElevatorSyncArgs = {
  elevatorBankId: Scalars['String']['input'];
};


export type MutationAddFloorArgs = {
  floorType: FloorTypeGql;
};


export type MutationAddFloorSyncArgs = {
  floorType: FloorTypeGql;
};


export type MutationAddPersonArgs = {
  block: Scalars['Float']['input'];
  destBlock: Scalars['Int']['input'];
  destFloor: Scalars['Int']['input'];
  floor: Scalars['Int']['input'];
};


export type MutationAddPersonSyncArgs = {
  block: Scalars['Float']['input'];
  destBlock: Scalars['Int']['input'];
  destFloor: Scalars['Int']['input'];
  floor: Scalars['Int']['input'];
};

export type PersonSnapshotGql = {
  readonly __typename?: 'PersonSnapshotGQL';
  readonly DrawColor: ReadonlyArray<Scalars['Int']['output']>;
  readonly currentFloorNum: Scalars['Int']['output'];
  readonly currentHorizontalPosition: Scalars['Blocks']['output'];
  readonly currentVerticalPosition: Scalars['Blocks']['output'];
  readonly destinationFloorNum: Scalars['Int']['output'];
  readonly destinationHorizontalPosition: Scalars['Blocks']['output'];
  readonly drawColor: ColorGql;
  readonly madFraction: Scalars['Float']['output'];
  readonly personId: Scalars['String']['output'];
  readonly state: PersonStateGql;
  readonly waitingTime: Scalars['Time']['output'];
};

export type PersonStateGql =
  | 'IDLE'
  | 'IN_ELEVATOR'
  | 'WAITING_FOR_ELEVATOR'
  | 'WALKING';

export type Query = {
  readonly __typename?: 'Query';
  readonly allPeople?: Maybe<ReadonlyArray<PersonSnapshotGql>>;
  readonly buildingState?: Maybe<BuildingSnapshotGql>;
  readonly gameTime: Scalars['Time']['output'];
  readonly hello: Scalars['String']['output'];
  readonly isRunning: Scalars['Boolean']['output'];
};

export type Subscription = {
  readonly __typename?: 'Subscription';
  readonly buildingStateStream?: Maybe<BuildingSnapshotGql>;
  readonly gameTimeStream: Scalars['Time']['output'];
};


export type SubscriptionBuildingStateStreamArgs = {
  intervalMs?: Scalars['Int']['input'];
};


export type SubscriptionGameTimeStreamArgs = {
  intervalMs?: Scalars['Int']['input'];
};

export type VerticalDirectionGql =
  | 'DOWN'
  | 'STATIONARY'
  | 'UP';
